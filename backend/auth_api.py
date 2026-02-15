"""
Authentication API Service

FastAPI application for password-based authentication endpoints.
Mounts at /auth in production.
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Import auth functions from auth_manager
from auth_manager import (
    create_customer,
    validate_login,
    generate_qr_token,
    verify_qr_token,
)

# Import session functions for creating sessions after auth
import sys
sys.path.insert(0, str(Path(__file__).parent))
from session_manager import create_session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Authentication API",
    description="Password-based authentication service",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class SignupRequest(BaseModel):
    """Request model for customer signup with password."""
    name: str = Field(..., description="Customer name")
    phone_number: str = Field(..., description="Phone number (must be unique)")
    password: str = Field(..., min_length=6, description="Password (minimum 6 characters)")
    age: Optional[int] = Field(default=None, ge=0, le=150, description="Age in years")
    gender: Optional[str] = Field(default=None, description="Gender")
    city: Optional[str] = Field(default=None, description="City")
    building_name: Optional[str] = Field(default=None, description="Building name")
    address_landmark: Optional[str] = Field(default=None, description="Address landmark")
    channel: str = Field(default="web", description="Channel: web, whatsapp, kiosk")


class PasswordLoginRequest(BaseModel):
    """Request model for password-based login."""
    phone_number: str = Field(..., description="Phone number")
    password: str = Field(..., description="Password")
    channel: str = Field(default="web", description="Channel: web, whatsapp, kiosk")


class QRInitRequest(BaseModel):
    """Request model for QR code initialization."""
    phone_number: str = Field(..., description="Phone number of logged-in user")


class QRVerifyRequest(BaseModel):
    """Request model for QR code verification."""
    qr_token: str = Field(..., description="QR token from scanned code")
    phone_number: str = Field(..., description="Phone number of the user scanning")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "auth"}


@app.post("/signup")
async def signup(request: SignupRequest):
    """Create a new customer account with password."""
    try:
        # Create customer with password
        customer_data = {
            "name": request.name,
            "phone_number": request.phone_number,
            "password": request.password,
            "age": request.age,
            "gender": request.gender,
            "city": request.city,
            "building_name": request.building_name,
            "address_landmark": request.address_landmark,
        }

        customer = create_customer(customer_data)

        # Create session for the new customer
        token, session = create_session(
            phone=request.phone_number,
            channel=request.channel,
            customer_id=str(customer.get("customer_id")),
            customer_profile=customer,
        )

        return JSONResponse(status_code=201, content={
            "message": "Account created successfully",
            "customer": customer,
            "session_token": token,
            "session": session,
        })

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/login")
async def login(request: PasswordLoginRequest):
    """Authenticate user with phone and password."""
    try:
        # Validate credentials
        result = validate_login(request.phone_number, request.password)
        
        if isinstance(result, tuple) and len(result) == 2:
            success, customer = result
        else:
            raise HTTPException(status_code=500, detail="Invalid login result format")
        
        if not success or not customer:
            raise HTTPException(status_code=401, detail="Invalid phone number or password")

        if not isinstance(customer, dict):
            raise HTTPException(status_code=500, detail=f"Customer data is not a dict: {type(customer)}")

        customer_id = customer.get("customer_id")
        if customer_id is None:
            raise HTTPException(status_code=500, detail="Customer ID not found")
        
        # Ensure customer_id is a string
        customer_id = str(customer_id)

        # Create session for authenticated user
        token, session = create_session(
            phone=request.phone_number,
            channel=request.channel,
            customer_id=customer_id,
            customer_profile=customer,
        )

        return JSONResponse(status_code=200, content={
            "message": "Login successful",
            "customer": customer,
            "session_token": token,
            "session": session,
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/qr-init")
async def qr_init(
    request: QRInitRequest,
    x_session_token: Optional[str] = Header(None, alias="X-Session-Token")
):
    """Generate QR token for kiosk authentication."""
    try:
        if not x_session_token:
            raise HTTPException(status_code=401, detail="Must be logged in to generate QR code")

        # Get session to verify user and get customer_id
        from session_manager import get_session
        try:
            session = get_session(x_session_token)
        except HTTPException:
            raise HTTPException(status_code=401, detail="Invalid session")

        customer_id = session.get("customer_id") or session.get("user_id")
        if not customer_id:
            raise HTTPException(status_code=400, detail="Customer ID not found in session")

        qr_token = generate_qr_token(request.phone_number, str(customer_id))

        return JSONResponse(status_code=200, content={
            "qr_token": qr_token,
            "customer_id": customer_id,
            "message": "QR token generated successfully",
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"QR init error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/qr-verify")
async def qr_verify(request: QRVerifyRequest):
    """Verify QR token and create session for kiosk."""
    try:
        # Verify QR token
        valid, customer_info = verify_qr_token(request.qr_token)

        if not valid or not customer_info:
            raise HTTPException(status_code=401, detail="Invalid or expired QR token")

        # Get customer record
        from db.repositories.customer_repo import get_customer_by_phone
        try:
            customer = get_customer_by_phone(customer_info['phone'])
        except:
            # Fallback: load from CSV
            import pandas as pd
            df = pd.read_csv(Path(__file__).parent / "data" / "customers.csv")
            matches = df[df['phone_number'].astype(str) == str(customer_info['phone'])]
            if len(matches) > 0:
                customer = matches.iloc[0].to_dict()
            else:
                customer = {"customer_id": customer_info['customer_id'], "phone_number": customer_info['phone']}

        # Create session for kiosk
        token, session = create_session(
            phone=customer_info['phone'],
            channel="kiosk",
            customer_id=str(customer.get("customer_id")),
            customer_profile=customer,
        )

        return JSONResponse(status_code=200, content={
            "message": "QR verification successful",
            "customer": customer,
            "session_token": token,
            "session": session,
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"QR verify error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled error in auth service: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"status": "error", "message": "Internal server error"})