# Redis utilities for Loyalty Agent

import redis
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Redis Configuration
REDIS_URL = os.getenv("REDIS_URL")

# Initialize Redis client
redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=5
) if REDIS_URL else None


def get_user_points(user_id: str) -> int:
    """Get loyalty points for a user from Redis"""
    if not redis_client:
        raise RuntimeError("Redis client not initialized")
    
    points = redis_client.get(f"user:{user_id}:points")
    return int(points) if points else 0


def update_user_points(user_id: str, new_points: int) -> bool:
    """Update loyalty points for a user in Redis"""
    if not redis_client:
        raise RuntimeError("Redis client not initialized")
    
    redis_client.set(f"user:{user_id}:points", new_points)
    return True


def deduct_points(user_id: str, points_to_deduct: int) -> dict:
    """
    Atomically deduct points from user's balance
    Returns: {"success": bool, "remaining_points": int, "deducted": int}
    """
    if not redis_client:
        raise RuntimeError("Redis client not initialized")
    
    current_points = get_user_points(user_id)
    
    if current_points < points_to_deduct:
        return {
            "success": False,
            "remaining_points": current_points,
            "deducted": 0,
            "error": "Insufficient points"
        }
    
    new_points = current_points - points_to_deduct
    update_user_points(user_id, new_points)
    
    return {
        "success": True,
        "remaining_points": new_points,
        "deducted": points_to_deduct
    }


def add_points(user_id: str, points_to_add: int) -> dict:
    """
    Add points to user's balance
    Returns: {"success": bool, "new_balance": int, "added": int}
    """
    if not redis_client:
        raise RuntimeError("Redis client not initialized")
    
    current_points = get_user_points(user_id)
    new_points = current_points + points_to_add
    update_user_points(user_id, new_points)
    
    return {
        "success": True,
        "new_balance": new_points,
        "added": points_to_add
    }


def validate_coupon(code: str) -> Optional[dict]:
    """
    Validate coupon code and return discount details
    Returns: {"code": str, "discount_percent": float, "min_purchase": float}
    """
    # Coupon database (in production, this would be in Redis/DB)
    coupons = {
        "ABFRL10": {"code": "ABFRL10", "discount_percent": 10.0, "min_purchase": 500.0},
        "ABFRL20": {"code": "ABFRL20", "discount_percent": 20.0, "min_purchase": 1000.0},
        "NEW50": {"code": "NEW50", "discount_percent": 50.0, "min_purchase": 2000.0},
        "SAVE15": {"code": "SAVE15", "discount_percent": 15.0, "min_purchase": 750.0},
        "WELCOME25": {"code": "WELCOME25", "discount_percent": 25.0, "min_purchase": 1500.0},
    }
    
    return coupons.get(code.upper())


def check_coupon_usage(user_id: str, coupon_code: str) -> bool:
    """Check if user has already used this coupon"""
    if not redis_client:
        raise RuntimeError("Redis client not initialized")
    
    key = f"coupon_usage:{user_id}:{coupon_code}"
    return redis_client.exists(key) > 0


def mark_coupon_used(user_id: str, coupon_code: str, expiry_days: int = 365) -> bool:
    """Mark coupon as used by user (with expiry)"""
    if not redis_client:
        raise RuntimeError("Redis client not initialized")
    
    key = f"coupon_usage:{user_id}:{coupon_code}"
    redis_client.setex(key, expiry_days * 24 * 3600, "1")
    return True
