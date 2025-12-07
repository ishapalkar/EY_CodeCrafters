# Payment Agent

Processes payments via UPI, Card, Wallet, and POS terminals with authorization/capture support.

## Main Endpoints

### Process Payment
```bash
POST /payment/process
{
  "user_id": "user123",
  "amount": 1350.0,
  "payment_method": "upi",
  "order_id": "ORDER123"
}
```

### Authorize & Capture Payment
```bash
POST /payment/authorize
POST /payment/capture
```

## Running

```bash
cd backend/agents/worker_agents/payment
python app.py
```

Server: `http://localhost:8003`
