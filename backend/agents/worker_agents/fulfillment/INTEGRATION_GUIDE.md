# Fulfillment Agent Integration Guide

This guide explains how to integrate the **Fulfillment Agent** with **Inventory Agent** and **Payment Agent** without modifying their existing code.

## Architecture Overview

```
┌─────────────────────────┐
│   Order Service         │
│  (or API Gateway)       │
└────────────┬────────────┘
             │
    ┌────────┴────────┐
    │                 │
    v                 v
┌──────────────┐  ┌──────────────┐
│ Inventory    │  │ Payment      │
│ Agent        │  │ Agent        │
│ :8002        │  │ :8003        │
└──────────────┘  └──────────────┘
    │                 │
    └────────┬────────┘
             │
    ┌────────v────────┐
    │  Fulfillment    │
    │  Agent          │
    │  :8004          │
    └─────────────────┘
```

## Integration Flow

### 1. Order Placement Flow

When an order is placed, the following sequence occurs:

```
┌─────────────┐
│  Order      │
│  Service    │
└──────┬──────┘
       │
       ├─[1] POST /hold (Inventory Agent)
       │     {sku, quantity, location, ttl}
       │
       ├─[2] POST /payment/process (Payment Agent)
       │     {user_id, amount, payment_method, order_id}
       │
       └─[3] POST /fulfillment/start (Fulfillment Agent)
             {order_id, inventory_hold_id, payment_transaction_id, ...}
```

**Step-by-step:**

1. **Inventory Agent** → `/hold` endpoint:
   - Reserves stock for the order
   - Returns `hold_id` (e.g., `"hold-550e8400-e29b-41d4-a716-446655440000"`)

2. **Payment Agent** → `/payment/process` endpoint:
   - Processes payment for the order
   - Returns `transaction_id` (e.g., `"TXN_ABC123XYZ789"`)

3. **Fulfillment Agent** → `/fulfillment/start` endpoint:
   - Receives `inventory_hold_id` and `payment_transaction_id`
   - Stores these IDs for later use during cancellation/return

### 2. Fulfillment Workflow

The fulfillment progresses through these states:

```
PROCESSING → PACKED → SHIPPED → OUT_FOR_DELIVERY → DELIVERED
```

Each state transition is made via the `/fulfillment/update-status` endpoint.

### 3. Cancellation or Return Flow

When an order is cancelled (before delivery) or returned (after delivery):

```
┌──────────────────────────┐
│ Fulfillment Agent        │
│ /cancel-order or         │
│ /process-return          │
└──────┬───────────────────┘
       │
       ├─[1] POST /release (Inventory Agent)
       │     {hold_id} ← retrieved from fulfillment record
       │     Release the inventory hold
       │
       └─[2] POST /payment/refund (Payment Agent)
             {transaction_id, amount, reason} ← retrieved from fulfillment record
             Process the refund
```

**Important:** The `inventory_hold_id` and `payment_transaction_id` are stored during `/fulfillment/start` and used later for cancellation/return.

## API Endpoints Reference

### Fulfillment Agent Endpoints

All endpoints are at `http://localhost:8004` (or your deployment URL).

#### 1. Start Fulfillment
**Endpoint:** `POST /fulfillment/start`

**Request:**
```json
{
  "order_id": "order_12345",
  "inventory_status": "RESERVED",
  "payment_status": "SUCCESS",
  "amount": 99.99,
  "inventory_hold_id": "hold-550e8400-e29b-41d4-a716-446655440000",
  "payment_transaction_id": "TXN_ABC123XYZ789"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Fulfillment started successfully",
  "fulfillment": {
    "fulfillment_id": "uuid",
    "order_id": "order_12345",
    "current_status": "PROCESSING",
    "tracking_id": "TRK-ABC123XYZ789",
    "courier_partner": "FedEx",
    "eta": "2025-12-11T12:30:45Z",
    "inventory_hold_id": "hold-550e8400-e29b-41d4-a716-446655440000",
    "payment_transaction_id": "TXN_ABC123XYZ789",
    ...
  }
}
```

#### 2. Update Status
**Endpoint:** `POST /fulfillment/update-status`

```json
{
  "order_id": "order_12345",
  "new_status": "PACKED"
}
```

#### 3. Mark Delivered
**Endpoint:** `POST /fulfillment/mark-delivered`

```json
{
  "order_id": "order_12345",
  "delivery_notes": "Left at front door"
}
```

#### 4. Cancel Order
**Endpoint:** `POST /fulfillment/cancel-order`

```json
{
  "order_id": "order_12345",
  "reason": "Customer requested cancellation",
  "refund_amount": 99.99
}
```

**What happens internally:**
- Calls `POST /release` on Inventory Agent with `hold_id`
- Calls `POST /payment/refund` on Payment Agent with `transaction_id`

#### 5. Process Return
**Endpoint:** `POST /fulfillment/process-return`

```json
{
  "order_id": "order_12345",
  "reason": "Item damaged",
  "refund_amount": 99.99
}
```

**What happens internally:**
- Calls `POST /release` on Inventory Agent with `hold_id`
- Calls `POST /payment/refund` on Payment Agent with `transaction_id`

### Related Agent Endpoints

#### Inventory Agent
- **Hold stock:** `POST /hold`
  ```json
  {
    "sku": "SKU123",
    "quantity": 1,
    "location": "online",
    "ttl": 300
  }
  ```
  Returns: `{hold_id, sku, quantity, location, remaining_stock, expires_at, status}`

- **Release stock:** `POST /release`
  ```json
  {
    "hold_id": "hold-550e8400-..."
  }
  ```
  Returns: `{hold_id, status, restored_stock}`

#### Payment Agent
- **Process payment:** `POST /payment/process`
  ```json
  {
    "user_id": "user_123",
    "amount": 99.99,
    "payment_method": "card",
    "order_id": "order_12345"
  }
  ```
  Returns: `{transaction_id, amount, payment_method, gateway_txn_id, cashback, status}`

- **Refund:** `POST /payment/refund`
  ```json
  {
    "transaction_id": "TXN_ABC123...",
    "amount": 99.99,
    "reason": "Order Cancellation"
  }
  ```
  Returns: `{refund_id, transaction_id, refund_amount, status}`

## Implementation in Your Order Service

Here's how to implement the full flow in your order/checkout service:

```python
import httpx

# Step 1: Hold inventory
inventory_response = await httpx.AsyncClient().post(
    "http://localhost:8002/hold",
    json={
        "sku": product_sku,
        "quantity": quantity,
        "location": "online",
        "ttl": 600
    }
)
hold_id = inventory_response.json()["hold_id"]

# Step 2: Process payment
payment_response = await httpx.AsyncClient().post(
    "http://localhost:8003/payment/process",
    json={
        "user_id": user_id,
        "amount": total_amount,
        "payment_method": "card",
        "order_id": order_id
    }
)
transaction_id = payment_response.json()["transaction_id"]

# Step 3: Start fulfillment
fulfillment_response = await httpx.AsyncClient().post(
    "http://localhost:8004/fulfillment/start",
    json={
        "order_id": order_id,
        "inventory_status": "RESERVED",
        "payment_status": "SUCCESS",
        "amount": total_amount,
        "inventory_hold_id": hold_id,
        "payment_transaction_id": transaction_id
    }
)
fulfillment = fulfillment_response.json()["fulfillment"]

# Now you have a complete order with:
# - Inventory reserved (hold_id)
# - Payment processed (transaction_id)
# - Fulfillment started (fulfillment_id)
```

## Agent Port Configuration

Update these ports if your agents run on different ports:

**In `fulfillment/app.py`:**
```python
INVENTORY_AGENT_URL = "http://localhost:8002"  # Change if needed
PAYMENT_AGENT_URL = "http://localhost:8003"    # Change if needed
```

## Running All Agents Locally

```bash
# Terminal 1: Inventory Agent
cd backend/agents/worker_agents/inventory
python -m uvicorn app:app --port 8002 --reload

# Terminal 2: Payment Agent
cd backend/agents/worker_agents/payment
python -m uvicorn app:app --port 8003 --reload

# Terminal 3: Fulfillment Agent
cd backend/agents/worker_agents/fulfillment
python -m uvicorn app:app --port 8004 --reload

# Terminal 4: Test Script
cd backend/agents/worker_agents/fulfillment
python test_integration.py  # (if available)
```

## Key Design Principles

1. **No Code Modifications**: Fulfillment Agent makes HTTP calls to existing endpoints. Inventory and Payment agents are unchanged.

2. **ID Passthrough**: The `inventory_hold_id` and `payment_transaction_id` are passed from the order service → fulfillment agent at start time, then used for cancellation/return.

3. **Idempotency**: Multiple cancellation or return requests for the same order are safe (the same hold_id and transaction_id are used).

4. **Error Handling**: If inventory release or refund fails, the fulfillment agent logs the error but doesn't crash. In production, implement retry logic.

5. **Event Logging**: All interactions are logged in the fulfillment record's `events_log` for audit trails.

## Error Scenarios

### Scenario 1: Inventory Agent Unavailable
- **What happens:** `inventory_agent_release_stock()` logs error and returns `False`
- **Result:** Order cancellation still proceeds (payment refund may complete)
- **Solution:** Implement retry logic or manual reconciliation process

### Scenario 2: Payment Agent Unavailable
- **What happens:** `payment_agent_initiate_refund()` logs error and returns `False`
- **Result:** Stock is released but refund fails
- **Solution:** Implement retry logic or manual refund process

### Scenario 3: Fulfillment Agent Restarts
- **What happens:** In-memory fulfillment records are lost
- **Solution:** Persist fulfillment records to a database in production

## Next Steps for Production

1. Replace in-memory storage with a database (PostgreSQL, MongoDB, etc.)
2. Add retry logic for external agent calls (exponential backoff, dead-letter queue)
3. Implement authentication/authorization between agents
4. Add comprehensive logging and monitoring
5. Set up health checks and service discovery
6. Implement circuit breaker pattern for external calls
7. Add request tracing (distributed tracing with Jaeger/DataDog)

## Testing Integration

Use the provided `test_example.py` to test:

```bash
# Start all three agents first, then:
python backend/agents/worker_agents/fulfillment/test_example.py
```

This runs:
- Complete fulfillment workflow
- Invalid transition rejection
- Cancellation with refund
- Returns after delivery
- Duplicate prevention
- Input validation
