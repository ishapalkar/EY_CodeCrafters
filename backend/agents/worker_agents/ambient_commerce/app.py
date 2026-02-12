# Ambient Commerce Integrator Agent - FastAPI Server
# Visual search for apparel products with intelligent matching and recommendations

import os
# Fix for OpenMP library conflict (must be set before importing torch/numpy)
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import uvicorn
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import requests
import re

from feature_extractor import FeatureExtractor
from index_builder import FAISSIndexBuilder
import redis_utils

app = FastAPI(
    title="Ambient Commerce Integrator Agent",
    description="Visual search and product matching using deep learning",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# GLOBAL STATE
# ==========================================

# Initialize index builder (lazy loading)
index_builder = None

# Use absolute paths for reliability
CURRENT_DIR = Path(__file__).parent
DATA_DIR = str((CURRENT_DIR / ".." / ".." / ".." / "data").resolve())
INDEX_DIR = str(CURRENT_DIR / "index_cache")

# Ensure index cache directory exists
Path(INDEX_DIR).mkdir(parents=True, exist_ok=True)


def get_index_builder(accuracy_mode: str = 'enhanced') -> FAISSIndexBuilder:
    """Get or initialize the index builder with specified accuracy mode."""
    global index_builder
    
    if index_builder is None:
        # Use 'enhanced' mode by default for better accuracy
        # Options: 'simple' (fast), 'enhanced' (balanced), 'ensemble' (best)
        index_builder = FAISSIndexBuilder(data_dir=DATA_DIR, accuracy_mode=accuracy_mode)
        
        # Try to load pre-built index
        index_path = os.path.join(INDEX_DIR, "products.index")
        metadata_path = os.path.join(INDEX_DIR, "products.metadata")
        
        if os.path.exists(index_path) and os.path.exists(metadata_path):
            try:
                index_builder.load_index(index_path, metadata_path)
                print("Loaded pre-built index from cache")
            except Exception as e:
                print(f"Failed to load cached index: {e}")
                print("Building new index...")
                index_builder.build_index()
                index_builder.save_index(index_path, metadata_path)
        else:
            print("Building index for the first time...")
            index_builder.build_index()
            index_builder.save_index(index_path, metadata_path)
    
    return index_builder


# ==========================================
# REQUEST/RESPONSE MODELS
# ==========================================

class VisualSearchRequest(BaseModel):
    image_path: str = Field(..., description="Path to the uploaded image")
    category: Optional[str] = Field(None, description="Filter by category (e.g., 'Apparel', 'Footwear')")
    subcategory: Optional[str] = Field(None, description="Filter by subcategory (e.g., 'Topwear', 'Shoes')")
    top_k: int = Field(default=1, ge=1, le=10, description="Number of top matches to return")
    similarity_threshold: float = Field(default=0.8, ge=0.0, le=1.0, description="Minimum similarity score")


class ProductVariant(BaseModel):
    sku: str
    brand: str
    product_name: str
    color: str
    size: List
    material: str
    price: float
    gender: str
    image_url: str


class MatchResult(BaseModel):
    matched_product_id: str
    product_name: str
    brand: str
    similarity_score: float
    color: str
    size: List
    material: str
    price: float
    image_url: str
    reasoning: str


class VisualSearchResponse(BaseModel):
    success: bool
    query_image: str
    num_matches: int
    best_match: Optional[MatchResult]
    alternative_matches: List[MatchResult]
    available_variants: List[ProductVariant]
    search_metadata: Dict
    message: str


class IndexBuildRequest(BaseModel):
    category: Optional[str] = Field(None, description="Category to index (e.g., 'Apparel')")
    subcategory: Optional[str] = Field(None, description="Subcategory to index")
    force_rebuild: bool = Field(default=False, description="Force rebuild even if index exists")
    accuracy_mode: str = Field(default='enhanced', description="Accuracy mode: 'simple', 'enhanced', or 'ensemble'")


class IndexInfoResponse(BaseModel):
    index_built: bool
    num_products: int
    index_path: str
    last_updated: Optional[str]


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def infer_color_from_name(product_name: str) -> Optional[str]:
    if not product_name:
        return None

    color_terms = [
        "black", "white", "red", "blue", "green", "yellow", "pink", "purple",
        "grey", "gray", "navy", "brown", "beige", "tan", "orange", "silver",
        "gold", "maroon", "olive", "teal", "turquoise", "coral", "violet",
        "indigo", "lavender", "cream", "off white", "off-white", "charcoal",
        "khaki", "mustard", "peach", "mint", "burgundy", "dandelion",
    ]

    matches = []
    for term in color_terms:
        pattern = r"\b" + re.escape(term).replace("\\ ", r"[\\s-]+") + r"\b"
        found = re.search(pattern, product_name, flags=re.IGNORECASE)
        if found:
            matches.append((found.start(), term))

    if not matches:
        return None

    matches.sort(key=lambda item: item[0])
    ordered = []
    for _, term in matches:
        normalized = " ".join(word.capitalize() for word in term.replace("-", " ").split())
        if normalized not in ordered:
            ordered.append(normalized)

    return " ".join(ordered)


def normalize_color(raw_color: Optional[str], product_name: str) -> str:
    if raw_color is None:
        inferred = infer_color_from_name(product_name)
        return inferred if inferred else "Neutral"

    color_text = str(raw_color).strip()
    if color_text.lower() in {"", "unknown", "n/a", "na", "none", "null", "nan"}:
        inferred = infer_color_from_name(product_name)
        return inferred if inferred else "Neutral"

    return color_text

def generate_reasoning(match: Dict, all_matches: List[Dict], similarity_threshold: float) -> str:
    """
    Generate human-readable reasoning for the match using Groq API for premium, unique descriptions.
    
    Args:
        match: The matched product
        all_matches: All matches found
        similarity_threshold: Threshold used for matching
        
    Returns:
        Reasoning string
    """
    score = match['similarity_score']
    brand = match['brand']
    product = match['product_name']
    color = normalize_color(match.get('color'), product)
    material = match.get('material', 'premium fabric')
    subcategory = match.get('subcategory', 'essentials')
    price = match.get('price', 0)
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    groq_model = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
    
    # Style variations for more diverse outputs
    style_approaches = [
        "luxury boutique",
        "trend-focused",
        "classic elegance",
        "modern minimalist",
        "lifestyle brand",
        "premium quality"
    ]
    
    # Use a combination of product attributes for randomization to ensure uniqueness
    seed = hash(f"{product}{color}{material}{price}")
    style = style_approaches[abs(seed) % len(style_approaches)]
    
    # Additional randomization: vary temperature and approach
    temp_variation = 0.85 + (abs(seed % 100) / 500.0)  # 0.85 to 1.05

    if groq_api_key:
        try:
            prompt = (
                f"You are an expert {style} stylist writing compelling product copy. "
                f"Craft a premium, personalized 3-4 sentence description for this item that makes the customer feel this is THE perfect match.\n\n"
                f"Product Details:\n"
                f"• Item: {brand} {product}\n"
                f"• Color: {color}\n"
                f"• Material: {material}\n"
                f"• Category: {subcategory}\n"
                f"• Price: ₹{price}\n"
                f"• Visual Match: {score:.1%}\n\n"
                f"Guidelines:\n"
                f"- Start by highlighting what makes THIS specific product special\n"
                f"- Emphasize the **{brand}** heritage and **{color}** appeal naturally\n"
                f"- Weave in lifestyle benefits and styling versatility\n"
                f"- Use 1-2 **bold phrases** for key features\n"
                f"- Sound exclusive yet approachable\n"
                f"- DO NOT mention 'match score' or 'similar to your image' - focus on product itself\n"
                f"- Make it feel personally curated for them\n"
                f"- Each product description must be UNIQUE - never repeat patterns"
            )

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {groq_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": groq_model,
                    "messages": [
                        {"role": "system", "content": f"You are a premium {style} fashion consultant known for personalized, compelling product storytelling."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": temp_variation,
                    "max_tokens": 150,
                    "top_p": 0.95,
                    "frequency_penalty": 0.6,
                    "presence_penalty": 0.4,
                },
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if content:
                return content.strip()
        except Exception as e:
            logger.warning(f"Groq API failed for {product}: {e}")

    # Premium fallback when Groq API is unavailable - focus on product benefits only
    # NO technical details, NO similarity scores - pure sales copy
    
    # Opening hooks that highlight the product
    opening_variants = [
        f"Discover the **{brand} {product}** – a standout piece that brings effortless style to your wardrobe.",
        f"Meet the **{brand} {product}** – crafted for those who appreciate quality and design.",
        f"The **{brand} {product}** is your go-to choice when you want to make a confident style statement.",
        f"Elevate your look with the **{brand} {product}** – where comfort meets contemporary design.",
        f"Introducing the **{brand} {product}** – designed to complement your unique style perfectly.",
    ]
    
    # Color/material highlights
    feature_variants = [
        f"The **{color}** shade adds a touch of sophistication, while the **{material}** ensures lasting comfort.",
        f"Beautifully finished in **{color}**, this piece features premium **{material}** for all-day wearability.",
        f"The rich **{color}** tone paired with quality **{material}** creates a timeless appeal.",
        f"Styled in an elegant **{color}** hue with carefully selected **{material}** – built to last.",
        f"A stunning **{color}** color combined with premium **{material}** makes this a wardrobe essential.",
    ]
    
    # Closing CTAs
    closing_variants = [
        "Perfect for both everyday wear and special occasions – add it to your collection today.",
        "Versatile enough for any look, refined enough to make you stand out.",
        "This is the piece you'll reach for again and again. Don't miss out.",
        "Ready to elevate your style game? This is your perfect match.",
        "A smart investment in quality and style that you'll love wearing.",
    ]
    
    # Build the description using varied combinations
    seed_val = abs(hash(f"{product}{color}"))
    opening = opening_variants[seed_val % len(opening_variants)]
    features = feature_variants[(seed_val // 10) % len(feature_variants)]
    closing = closing_variants[(seed_val // 100) % len(closing_variants)]
    
    # Only mention brand reputation if it's a known brand (not "Unknown")
    if brand and brand != "Unknown":
        brand_note = f" **{brand}** brings decades of craftsmanship and style innovation to every piece."
        return f"{opening} {features}{brand_note} {closing}"
    
    return f"{opening} {features} {closing}"


def select_best_match_with_brand_preference(matches: List[Dict], preferred_brand: Optional[str] = None) -> Dict:
    """
    Select the best match, preferring the same brand if multiple matches exist.
    
    Args:
        matches: List of matched products
        preferred_brand: Brand to prefer (if any)
        
    Returns:
        Best matched product
    """
    if not matches:
        return None
    
    if len(matches) == 1:
        return matches[0]
    
    # If preferred brand specified, prioritize it
    if preferred_brand:
        brand_matches = [m for m in matches if m['brand'].lower() == preferred_brand.lower()]
        if brand_matches:
            return max(brand_matches, key=lambda x: x['similarity_score'])
    
    # Group by brand
    brands = {}
    for match in matches:
        brand = match['brand']
        if brand not in brands:
            brands[brand] = []
        brands[brand].append(match)
    
    # If one brand has multiple matches and highest score, prefer it
    best_by_brand = {}
    for brand, brand_matches in brands.items():
        best_by_brand[brand] = max(brand_matches, key=lambda x: x['similarity_score'])
    
    # Select the brand with the best score
    return max(best_by_brand.values(), key=lambda x: x['similarity_score'])


# ==========================================
# ENDPOINTS
# ==========================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Ambient Commerce Integrator",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/index/info", response_model=IndexInfoResponse)
async def get_index_info():
    """Get information about the current index."""
    index_path = os.path.join(INDEX_DIR, "products.index")
    metadata_path = os.path.join(INDEX_DIR, "products.metadata")
    
    index_exists = os.path.exists(index_path) and os.path.exists(metadata_path)
    
    last_updated = None
    num_products = 0
    
    if index_exists:
        last_updated = datetime.fromtimestamp(os.path.getmtime(index_path)).isoformat()
        builder = get_index_builder()
        num_products = builder.index.ntotal if builder.index else 0
    
    return IndexInfoResponse(
        index_built=index_exists,
        num_products=num_products,
        index_path=index_path,
        last_updated=last_updated
    )


@app.post("/index/build")
async def build_index(request: IndexBuildRequest):
    """
    Build or rebuild the FAISS index.
    This can take several minutes depending on the number of products.
    """
    global index_builder
    
    index_path = os.path.join(INDEX_DIR, "products.index")
    metadata_path = os.path.join(INDEX_DIR, "products.metadata")
    
    # Check if index already exists
    if not request.force_rebuild and os.path.exists(index_path):
        return {
            "success": True,
            "message": "Index already exists. Use force_rebuild=true to rebuild.",
            "index_path": index_path
        }
    
    try:
        # Initialize new builder with specified accuracy mode
        builder = FAISSIndexBuilder(data_dir=DATA_DIR, accuracy_mode=request.accuracy_mode)
        
        # Build index with filters
        num_indexed = builder.build_index(
            category_filter=request.category,
            subcategory_filter=request.subcategory
        )
        
        # Save index
        builder.save_index(index_path, metadata_path)
        
        # Update global builder
        index_builder = builder
        
        return {
            "success": True,
            "message": f"Index built successfully with {num_indexed} products",
            "num_products": num_indexed,
            "index_path": index_path,
            "filters": {
                "category": request.category,
                "subcategory": request.subcategory
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build index: {str(e)}")


@app.post("/search/upload", response_model=VisualSearchResponse)
async def search_by_upload(
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    subcategory: Optional[str] = Form(None),
    top_k: int = Form(3),
    similarity_threshold: float = Form(0.8)
):
    """
    Upload an image and search for similar products.
    Returns top matches if similarity < threshold, otherwise returns best match.
    """
    # Save uploaded file temporarily
    temp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir, file.filename)
    
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Perform search
        search_request = VisualSearchRequest(
            image_path=temp_file_path,
            category=category,
            subcategory=subcategory,
            top_k=top_k,
            similarity_threshold=similarity_threshold
        )
        result = await search_product(search_request)
        
        return result
    
    finally:
        # Cleanup
        try:
            shutil.rmtree(temp_dir)
        except:
            pass


@app.post("/search", response_model=VisualSearchResponse)
async def search_product(request: VisualSearchRequest):
    """
    Search for products similar to the provided image.
    
    Features:
    - If similarity < threshold, returns top_k matches
    - Prefers same brand if multiple matches
    - Returns all variants of matched product
    - Provides human-readable reasoning
    """
    # Extract parameters from request
    image_path = request.image_path
    category = request.category
    subcategory = request.subcategory
    top_k = request.top_k
    similarity_threshold = request.similarity_threshold
    
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail=f"Image not found: {image_path}")
    
    try:
        # Get index builder
        builder = get_index_builder()
        
        # Search for similar products with reranking for better accuracy
        matches = builder.search(image_path, top_k=top_k, rerank=True)
        
        if not matches:
            return VisualSearchResponse(
                success=False,
                query_image=image_path,
                num_matches=0,
                best_match=None,
                alternative_matches=[],
                available_variants=[],
                search_metadata={},
                message="No matching products found"
            )
        
        # Determine if we should return multiple matches
        best_score = matches[0]['similarity_score']
        return_multiple = best_score < similarity_threshold
        
        # Select best match (with brand preference)
        best_match_data = select_best_match_with_brand_preference(matches)
        
        # Generate reasoning
        reasoning = generate_reasoning(best_match_data, matches, similarity_threshold)
        
        # Create best match result
        best_match = MatchResult(
            matched_product_id=best_match_data['sku'],
            product_name=best_match_data['product_name'],
            brand=best_match_data['brand'],
            similarity_score=best_match_data['similarity_score'],
            color=best_match_data['color'],
            size=best_match_data['size'],
            material=best_match_data['material'],
            price=best_match_data['price'],
            image_url=best_match_data['image_url'],
            reasoning=reasoning
        )
        
        # Create alternative matches if similarity is low
        alternative_matches = []
        if return_multiple:
            for match_data in matches[1:]:
                alt_reasoning = generate_reasoning(match_data, matches, similarity_threshold)
                alt_match = MatchResult(
                    matched_product_id=match_data['sku'],
                    product_name=match_data['product_name'],
                    brand=match_data['brand'],
                    similarity_score=match_data['similarity_score'],
                    color=match_data['color'],
                    size=match_data['size'],
                    material=match_data['material'],
                    price=match_data['price'],
                    image_url=match_data['image_url'],
                    reasoning=alt_reasoning
                )
                alternative_matches.append(alt_match)
        
        # Get all variants of the best matched product
        variants_data = builder.get_all_variants(best_match_data['sku'])
        variants = [ProductVariant(**v) for v in variants_data]
        
        # Prepare response
        return VisualSearchResponse(
            success=True,
            query_image=image_path,
            num_matches=len(matches),
            best_match=best_match,
            alternative_matches=alternative_matches,
            available_variants=variants,
            search_metadata={
                "similarity_threshold": similarity_threshold,
                "top_k_requested": top_k,
                "returned_multiple": return_multiple,
                "num_variants": len(variants),
                "category_filter": category,
                "subcategory_filter": subcategory
            },
            message=f"Found {len(matches)} matching products" if return_multiple else "Found exact match"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/product/{sku}/variants")
async def get_product_variants(sku: str):
    """Get all variants of a product by SKU."""
    try:
        builder = get_index_builder()
        variants = builder.get_all_variants(sku)
        
        if not variants:
            raise HTTPException(status_code=404, detail=f"No variants found for SKU: {sku}")
        
        return {
            "success": True,
            "sku": sku,
            "num_variants": len(variants),
            "variants": variants
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cache/clear")
async def clear_cache():
    """Clear Redis cache (if implemented)."""
    try:
        # Clear Redis cache if using
        # redis_utils.clear_cache()
        
        return {
            "success": True,
            "message": "Cache cleared successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ambient Commerce Integrator Agent")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8017, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    uvicorn.run(
        "app:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )
