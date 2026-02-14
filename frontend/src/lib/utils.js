import { clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import { API_BASE_URL } from "../config/api"

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}
/**
 * Resolve image URLs to proper URLs
 * Prioritizes Supabase full URLs (https://...) and uses them directly
 * Falls back to local backend for relative paths
 */
export function resolveImageUrl(imagePath) {
  if (!imagePath) return null;
  
  // If it's already a full HTTPS URL (likely from Supabase), use as-is
  if (imagePath.startsWith('https://')) {
    return imagePath;
  }
  
  // If it's an HTTP URL, also use as-is
  if (imagePath.startsWith('http://')) {
    return imagePath;
  }
  
  // Data URI - use as-is
  if (imagePath.startsWith('data:')) {
    return imagePath;
  }
  
  // Relative path from CSV - serve from frontend public folder
  // Convert CSV format (product1.jpg) to actual filename format (product_1.jpeg)
  let cleanPath = imagePath.replace(/\\/g, '/').replace(/^\/+/, '');
  cleanPath = cleanPath.replace(/^product_images\//, '');
  
  // Convert product1.jpg to product_1.jpeg
  cleanPath = cleanPath.replace(/^product(\d+)\.jpg$/, 'product_$1.jpeg');
  
  return `/product_images/${cleanPath}`;
}