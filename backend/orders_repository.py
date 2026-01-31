"""Utilities for persisting order records to the shared CSV dataset."""

from __future__ import annotations

import csv
import json
import logging
import re
from pathlib import Path
from threading import Lock
from typing import Dict, Iterable, Any, List

from db import supabase_client

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent / "data"
ORDERS_FILE = DATA_DIR / "orders.csv"
FIELDNAMES: Iterable[str] = (
    "order_id",
    "customer_id",
    "items",
    "total_amount",
    "status",
    "created_at",
)

_WRITE_LOCK = Lock()
_SUPABASE_TABLE = "orders"
_NUMERIC_FIELDS = {"total_amount"}
_ORDER_ID_PATTERN = re.compile(r"^ORD\d{6}$")


def _load_existing_rows() -> Dict[str, Dict[str, str]]:
    """Return existing order rows keyed by order_id."""
    if not ORDERS_FILE.exists():
        return {}

    with ORDERS_FILE.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        return {row["order_id"]: row for row in reader if row.get("order_id")}


def is_valid_order_id(order_id: str | None) -> bool:
    return bool(order_id) and bool(_ORDER_ID_PATTERN.match(order_id))


def _generate_next_order_id(rows: Dict[str, Dict[str, str]]) -> str:
    max_seq = 0
    for order_id in rows.keys():
        match = _ORDER_ID_PATTERN.match(order_id)
        if match:
            max_seq = max(max_seq, int(order_id[3:]))
    return f"ORD{max_seq + 1:06d}"


def generate_next_order_id() -> str:
    with _WRITE_LOCK:
        rows = _load_existing_rows()
        return _generate_next_order_id(rows)


def get_order(order_id: str) -> Dict[str, Any] | None:
    """Retrieve an order by order_id from the CSV file.
    
    Args:
        order_id: The order ID to retrieve
        
    Returns:
        Order dict with parsed items as list/dict, or None if not found
    """
    if not order_id:
        return None
    
    with _WRITE_LOCK:
        rows = _load_existing_rows()
        row = rows.get(order_id)
        
        if not row:
            return None
        
        # Parse items from JSON string if needed
        result = dict(row)
        if result.get("items"):
            try:
                result["items"] = json.loads(result["items"])
            except json.JSONDecodeError:
                pass
        
        return result


def upsert_order_record(record: Dict[str, Any]) -> None:
    """Insert or update an order entry in orders.csv in a threadsafe way."""
    if "order_id" not in record or not record["order_id"]:
        raise ValueError("record must include a non-empty order_id")

    logger.info(f"📝 Upserting order: {record.get('order_id')}")

    csv_payload = dict(record)
    supabase_payload = dict(record)
    
    # Ensure items is JSON string if it's a dict/list
    if isinstance(csv_payload.get("items"), (dict, list)):
        csv_payload["items"] = json.dumps(csv_payload["items"])
        logger.debug(f"   Serialized items to JSON")

    with _WRITE_LOCK:
        logger.debug(f"   Acquired write lock")
        rows = _load_existing_rows()
        logger.debug(f"   Loaded {len(rows)} existing rows")
        
        def _csv_value(field: str, value: Any) -> str:
            if value is None:
                return ""
            return str(value)

        rows[csv_payload["order_id"]] = {
            field: _csv_value(field, csv_payload.get(field, ""))
            for field in FIELDNAMES
        }
        logger.debug(f"   Updated row for order_id")

        ORDERS_FILE.parent.mkdir(parents=True, exist_ok=True)
        logger.debug(f"   Ensured directory exists: {ORDERS_FILE.parent}")
        
        with ORDERS_FILE.open("w", encoding="utf-8", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows.values())
            logger.info(f"✅ Written {len(rows)} orders to {ORDERS_FILE}")

    _sync_to_supabase(supabase_payload)


def _prepare_supabase_payload(record: Dict[str, Any]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    for field in FIELDNAMES:
        value = record.get(field)
        if value in (None, ""):
            payload[field] = None
            continue

        if field == "items":
            if isinstance(value, str):
                try:
                    payload[field] = json.loads(value)
                except json.JSONDecodeError:
                    payload[field] = value
            else:
                payload[field] = value
        elif field in _NUMERIC_FIELDS:
            try:
                payload[field] = float(value)
            except (TypeError, ValueError):
                payload[field] = None
        else:
            payload[field] = value

    return payload


def _sync_to_supabase(record: Dict[str, Any]) -> None:
    if not supabase_client.is_write_enabled():
        logger.warning(f"[orders_repository] Supabase write is DISABLED - order {record.get('order_id')} NOT synced")
        return

    payload = _prepare_supabase_payload(record)

    try:
        supabase_client.upsert(
            _SUPABASE_TABLE,
            payload,
            conflict_column="order_id",
        )
        logger.info("[orders_repository] ✅ Synced order %s to Supabase", record.get("order_id"))
    except Exception as exc:
        logger.warning(
            "[orders_repository] ❌ Failed to sync order %s to Supabase: %s",
            record.get("order_id"),
            exc,
        )
