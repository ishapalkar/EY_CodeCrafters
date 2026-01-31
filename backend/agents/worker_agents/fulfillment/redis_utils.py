"""
Redis utilities for Fulfillment Agent

Handles persistent storage of fulfillment records, event logs, and tracking data
using Redis hash structures and sorted sets for efficient querying.
"""

import redis
import json
import os
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Redis Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize Redis client
redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=5
) if REDIS_URL else None

# Expiry time for fulfillment records (90 days)
FULFILLMENT_TTL = 90 * 24 * 3600


# ==========================================
# REDIS KEY PATTERNS
# ==========================================

def _fulfillment_key(order_id: str) -> str:
    """Generate Redis key for fulfillment record."""
    return f"fulfillment:{order_id}"


def _order_tracking_key(order_id: str) -> str:
    """Generate Redis key for order tracking (faster lookups)."""
    return f"order:tracking:{order_id}"


def _events_key(order_id: str) -> str:
    """Generate Redis key for fulfillment events list."""
    return f"fulfillment:events:{order_id}"


def _orders_index_key() -> str:
    """Generate Redis key for all orders (sorted set by timestamp)."""
    return "fulfillment:orders:index"


def _status_index_key(status: str) -> str:
    """Generate Redis key for orders by status (e.g., PROCESSING, SHIPPED, DELIVERED)."""
    return f"fulfillment:orders:status:{status}"


# ==========================================
# HEALTH CHECK
# ==========================================

def check_redis_health() -> bool:
    """Check if Redis is connected and healthy."""
    try:
        if redis_client:
            redis_client.ping()
            return True
    except Exception:
        pass
    return False


# ==========================================
# FULFILLMENT RECORD OPERATIONS
# ==========================================

def store_fulfillment(order_id: str, fulfillment_data: Dict[str, Any]) -> bool:
    """
    Store fulfillment record in Redis.
    
    Uses hash structure for efficient storage and retrieval.
    Also maintains indexes for fast lookups by status.
    
    Args:
        order_id: Order ID
        fulfillment_data: Fulfillment record dictionary
    
    Returns:
        True if successful
    """
    if not redis_client:
        raise RuntimeError("Redis client not initialized")
    
    key = _fulfillment_key(order_id)
    
    # Convert nested structures to JSON strings
    data_to_store = {}
    for field, value in fulfillment_data.items():
        if isinstance(value, (dict, list)):
            data_to_store[field] = json.dumps(value)
        else:
            data_to_store[field] = str(value) if value is not None else ""
    
    # Store as hash
    redis_client.hset(key, mapping=data_to_store)
    
    # Set expiry
    redis_client.expire(key, FULFILLMENT_TTL)
    
    # Add to orders index (sorted by timestamp)
    timestamp = datetime.utcnow().timestamp()
    redis_client.zadd(_orders_index_key(), {order_id: timestamp})
    
    # Add to status index
    status = fulfillment_data.get("current_status", "PROCESSING")
    redis_client.sadd(_status_index_key(status), order_id)
    
    return True


def get_fulfillment(order_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve fulfillment record from Redis.
    
    Args:
        order_id: Order ID
    
    Returns:
        Fulfillment record dictionary or None if not found
    """
    if not redis_client:
        raise RuntimeError("Redis client not initialized")
    
    key = _fulfillment_key(order_id)
    
    if not redis_client.exists(key):
        return None
    
    # Get all fields from hash
    data = redis_client.hgetall(key)
    
    # Convert JSON strings back to objects
    for field in ["events_log", "data"]:
        if field in data and data[field]:
            try:
                data[field] = json.loads(data[field])
            except (json.JSONDecodeError, TypeError):
                pass
    
    return data if data else None


def update_fulfillment_status(order_id: str, new_status: str, timestamp: str) -> bool:
    """
    Update fulfillment status and timestamp.
    
    Also updates status indexes for fast lookups.
    
    Args:
        order_id: Order ID
        new_status: New status value
        timestamp: Timestamp field to update (e.g., "packed_at", "shipped_at")
    
    Returns:
        True if successful
    """
    if not redis_client:
        raise RuntimeError("Redis client not initialized")
    
    key = _fulfillment_key(order_id)
    
    # Update status and timestamp
    redis_client.hset(key, mapping={
        "current_status": new_status,
        timestamp: datetime.utcnow().isoformat() + "Z"
    })
    
    # Update status indexes
    old_status = redis_client.hget(key, "current_status")
    if old_status:
        redis_client.srem(_status_index_key(old_status), order_id)
    
    redis_client.sadd(_status_index_key(new_status), order_id)
    
    return True


def add_fulfillment_event(order_id: str, event_data: Dict[str, Any]) -> bool:
    """
    Add an event to fulfillment event log.
    
    Stores events as a JSON list in a separate key for easy retrieval and updates.
    
    Args:
        order_id: Order ID
        event_data: Event dictionary with event_type, timestamp, details
    
    Returns:
        True if successful
    """
    if not redis_client:
        raise RuntimeError("Redis client not initialized")
    
    events_key = _events_key(order_id)
    
    # Get current events
    events_json = redis_client.get(events_key)
    events = json.loads(events_json) if events_json else []
    
    # Append new event
    events.append(event_data)
    
    # Store updated events list
    redis_client.set(events_key, json.dumps(events))
    redis_client.expire(events_key, FULFILLMENT_TTL)
    
    return True


def get_fulfillment_events(order_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve all events for a fulfillment.
    
    Args:
        order_id: Order ID
    
    Returns:
        List of event dictionaries
    """
    if not redis_client:
        raise RuntimeError("Redis client not initialized")
    
    events_key = _events_key(order_id)
    events_json = redis_client.get(events_key)
    
    return json.loads(events_json) if events_json else []


# ==========================================
# TRACKING AND INDEXING
# ==========================================

def get_orders_by_status(status: str, limit: int = 100) -> List[str]:
    """
    Get all orders with a specific fulfillment status.
    
    Args:
        status: Fulfillment status (e.g., "PROCESSING", "SHIPPED", "DELIVERED")
        limit: Maximum number of orders to return
    
    Returns:
        List of order IDs
    """
    if not redis_client:
        raise RuntimeError("Redis client not initialized")
    
    key = _status_index_key(status)
    order_ids = redis_client.smembers(key)
    
    return list(order_ids)[:limit]


def get_recent_orders(limit: int = 50) -> List[str]:
    """
    Get recent orders (sorted by timestamp, newest first).
    
    Args:
        limit: Maximum number of orders to return
    
    Returns:
        List of order IDs in reverse chronological order
    """
    if not redis_client:
        raise RuntimeError("Redis client not initialized")
    
    key = _orders_index_key()
    # Get last `limit` orders (newest first)
    order_ids = redis_client.zrevrange(key, 0, limit - 1)
    
    return list(order_ids)


def order_exists(order_id: str) -> bool:
    """
    Check if a fulfillment record exists for an order.
    
    Args:
        order_id: Order ID
    
    Returns:
        True if fulfillment exists, False otherwise
    """
    if not redis_client:
        raise RuntimeError("Redis client not initialized")
    
    return redis_client.exists(_fulfillment_key(order_id)) > 0


def get_fulfillment_count(status: str = None) -> int:
    """
    Get count of fulfillments, optionally filtered by status.
    
    Args:
        status: Optional status filter
    
    Returns:
        Count of fulfillment records
    """
    if not redis_client:
        raise RuntimeError("Redis client not initialized")
    
    if status:
        return redis_client.scard(_status_index_key(status))
    else:
        return redis_client.zcard(_orders_index_key())


# ==========================================
# CLEANUP AND MAINTENANCE
# ==========================================

def delete_fulfillment(order_id: str) -> bool:
    """
    Delete a fulfillment record and associated data.
    
    Useful for testing or data cleanup.
    
    Args:
        order_id: Order ID
    
    Returns:
        True if successful
    """
    if not redis_client:
        raise RuntimeError("Redis client not initialized")
    
    # Get current status to remove from status index
    fulfillment = get_fulfillment(order_id)
    if fulfillment:
        status = fulfillment.get("current_status")
        if status:
            redis_client.srem(_status_index_key(status), order_id)
    
    # Delete fulfillment record
    redis_client.delete(_fulfillment_key(order_id))
    
    # Delete events
    redis_client.delete(_events_key(order_id))
    
    # Remove from orders index
    redis_client.zrem(_orders_index_key(), order_id)
    
    return True


def flush_all() -> bool:
    """
    Delete all fulfillment data from Redis.
    
    WARNING: Use only in testing/development!
    
    Returns:
        True if successful
    """
    if not redis_client:
        raise RuntimeError("Redis client not initialized")
    
    # Get all keys matching our patterns
    patterns = [
        "fulfillment:*",
        "order:tracking:*",
        "fulfillment:orders:*"
    ]
    
    for pattern in patterns:
        for key in redis_client.scan_iter(match=pattern):
            redis_client.delete(key)
    
    
    return True


# ==========================================
# SCANNING OPERATIONS
# ==========================================

def scan_fulfillments(cursor: int = 0, count: int = 100) -> tuple:
    """
    Scan all fulfillment keys in Redis.
    
    Args:
        cursor: Redis scan cursor (start with 0)
        count: Number of keys to return per iteration
    
    Returns:
        Tuple of (next_cursor, list_of_order_ids)
    """
    if not redis_client:
        raise RuntimeError("Redis client not initialized")
    
    try:
        cursor, keys = redis_client.scan(cursor, match="fulfillment:*", count=count)
        order_ids = []
        for key in keys:
            if isinstance(key, bytes):
                order_id = key.decode('utf-8').replace("fulfillment:", "")
            else:
                order_id = key.replace("fulfillment:", "")
            order_ids.append(order_id)
        return cursor, order_ids
    except Exception as e:
        print(f"Error scanning fulfillments: {e}")
        return 0, []


def get_redis_connection():
    """Get the Redis client connection."""
    if not redis_client:
        raise RuntimeError("Redis client not initialized")
    return redis_client


# ==========================================
# STATISTICS AND MONITORING
# ==========================================

def get_fulfillment_stats() -> Dict[str, Any]:
    """
    Get fulfillment statistics.
    
    Returns:
        Dictionary with counts by status and total
    """
    if not redis_client:
        raise RuntimeError("Redis client not initialized")
    
    statuses = ["PROCESSING", "PACKED", "SHIPPED", "OUT_FOR_DELIVERY", "DELIVERED"]
    stats = {
        "total": get_fulfillment_count(),
        "by_status": {}
    }
    
    for status in statuses:
        stats["by_status"][status] = get_fulfillment_count(status)
    
    return stats

