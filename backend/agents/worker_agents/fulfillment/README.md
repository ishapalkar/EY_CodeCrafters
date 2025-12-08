# Fulfillment Agent

A FastAPI-based fulfillment management service for ecommerce orders with state management, logistics coordination, and integrations with inventory and payment agents.

## Features

- **Order Fulfillment Workflow**: Enforced state transitions (PROCESSING → PACKED → SHIPPED → OUT_FOR_DELIVERY → DELIVERED)
- **Logistics Coordination**: Automatic tracking ID generation, courier partner assignment, and ETA calculation
- **Inventory Integration**: Release stock on cancellations/returns via `inventory_agent.release_stock()`
- **Payment Integration**: Initiate refunds on cancellations/returns via `payment_agent.initiate_refund()`
- **Event Logging**: Complete audit trail of all fulfillment events
- **Idempotency**: Prevents duplicate processing and ensures reliable operations

## Installation

```bash
pip install fastapi uvicorn pydantic
```

## Running the Agent

From the repo root:

```bash
python -m uvicorn agents.worker_agents.fulfillment.app:app --reload --port 8004
```

Or directly:

```bash
cd backend/agents/worker_agents/fulfillment
uvicorn app:app --reload --port 8004
```

## API Endpoints

### 1. Start Fulfillment
**POST** `/fulfillment/start`

Initiates fulfillment for an order. Validates that:
- Order hasn't been processed yet (idempotency)
- Inventory status is "RESERVED"
- Payment status is "SUCCESS"

```json
{
  "order_id": "order_12345",
  "inventory_status": "RESERVED",
  "payment_status": "SUCCESS",
  "amount": 99.99
}
```

Response:
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
    "created_at": "2025-12-08T08:00:00Z",
    "processing_at": "2025-12-08T08:00:00Z",
    "events_log": [...]
  }
}
```

### 2. Update Status
**POST** `/fulfillment/update-status`

Transitions fulfillment to the next status in the workflow.

```json
{
  "order_id": "order_12345",
  "new_status": "PACKED"
}
```

Valid transitions:
- PROCESSING → PACKED
- PACKED → SHIPPED
- SHIPPED → OUT_FOR_DELIVERY
- OUT_FOR_DELIVERY → DELIVERED

### 3. Mark Delivered
**POST** `/fulfillment/mark-delivered`

Convenience endpoint to mark an order as delivered (validates it's OUT_FOR_DELIVERY).

```json
{
  "order_id": "order_12345",
  "delivery_notes": "Left at front door"
}
```

### 4. Handle Failed Delivery
**POST** `/fulfillment/handle-failed-delivery`

Records a failed delivery attempt (logs event, doesn't change status).

```json
{
  "order_id": "order_12345",
  "reason": "Address not found"
}
```

### 5. Cancel Order
**POST** `/fulfillment/cancel-order`

Cancels an order and processes refund:
- Calls `inventory_agent.release_stock(order_id)`
- Calls `payment_agent.initiate_refund(order_id, amount)`

```json
{
  "order_id": "order_12345",
  "reason": "Customer requested",
  "refund_amount": 99.99
}
```

**Cannot cancel if already delivered.**

### 6. Process Return
**POST** `/fulfillment/process-return`

Processes a return after delivery:
- Calls `inventory_agent.release_stock(order_id)`
- Calls `payment_agent.initiate_refund(order_id, amount)`

```json
{
  "order_id": "order_12345",
  "reason": "Item damaged",
  "refund_amount": 99.99
}
```

**Only allowed for delivered orders.**

### 7. Get Fulfillment Record
**GET** `/fulfillment/{order_id}`

Retrieves the complete fulfillment record for an order.

### 8. Get Fulfillment Status
**GET** `/fulfillment-status/{order_id}`

Retrieves just the current status, tracking, and ETA.

## Data Model

### FulfillmentRecord

```python
{
  "fulfillment_id": "uuid",
  "order_id": "str",
  "current_status": "PROCESSING|PACKED|SHIPPED|OUT_FOR_DELIVERY|DELIVERED",
  "tracking_id": "str",
  "courier_partner": "FedEx|UPS|Amazon Logistics|DHL|Local Courier",
  "eta": "ISO datetime string",
  "created_at": "ISO datetime string",
  "processing_at": "ISO datetime string | null",
  "packed_at": "ISO datetime string | null",
  "shipped_at": "ISO datetime string | null",
  "out_for_delivery_at": "ISO datetime string | null",
  "delivered_at": "ISO datetime string | null",
  "cancellation_reason": "str | null",
  "return_reason": "str | null",
  "events_log": [
    {
      "event_type": "FULFILLMENT_STARTED|STATUS_UPDATED|DELIVERY_FAILED|...",
      "timestamp": "ISO datetime string",
      "details": {}
    }
  ]
}
```

## Key Validations

✅ **Prevents skipping status steps**: Only allows sequential transitions
✅ **Prevents duplicate processing**: Rejects start requests for orders already in fulfillment
✅ **Idempotent**: External agent calls are safely repeatable
✅ **Validates order state**: Checks inventory and payment status before fulfillment
✅ **Terminal states**: Delivered orders cannot be modified

## Integration Points

### External Agent Calls

The agent stubs the following calls (to be integrated with actual HTTP endpoints):

```python
# Release inventory stock (for cancellations/returns)
await inventory_agent_release_stock(order_id)

# Initiate payment refund (for cancellations/returns)
await payment_agent_initiate_refund(order_id, amount)
```

Replace the stubs in `app.py` with actual HTTP calls to the respective agents.

## Event Log

All state changes are recorded in the `events_log` with:
- Event type (FULFILLMENT_STARTED, STATUS_UPDATED, DELIVERY_FAILED, etc.)
- Timestamp
- Event-specific details (old status, new status, reasons, amounts, etc.)

## Testing

Example curl commands:

```bash
# Start fulfillment
curl -X POST http://localhost:8004/fulfillment/start \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "order_12345",
    "inventory_status": "RESERVED",
    "payment_status": "SUCCESS",
    "amount": 99.99
  }'

# Update status
curl -X POST http://localhost:8004/fulfillment/update-status \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "order_12345",
    "new_status": "PACKED"
  }'

# Get fulfillment
curl http://localhost:8004/fulfillment/order_12345

# Cancel order
curl -X POST http://localhost:8004/fulfillment/cancel-order \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "order_12345",
    "reason": "Customer request",
    "refund_amount": 99.99
  }'
```

## Architecture Notes

- **In-memory storage**: Uses dictionaries for fast development/testing. Replace with database in production.
- **No database dependency**: Simplifies development but data is lost on restart.
- **Async-ready**: All endpoints use async handlers for future scaling.
- **Courier selection**: Randomly assigns from predefined partners.
- **ETA calculation**: Base 3 days + random 0-48 hours for realistic variation.

## Next Steps

1. Replace stub functions with actual HTTP calls to inventory and payment agents
2. Add database persistence (SQLAlchemy, MongoDB, etc.)
3. Add authentication/authorization
4. Implement retry logic for external agent calls
5. Add metrics and monitoring
