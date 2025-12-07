# Loyalty Agent

Manages loyalty points, coupons, and time-based promotions.

## Main Endpoints

### Apply Loyalty Benefits
```bash
POST /loyalty/apply
{
  "user_id": "user123",
  "cart_total": 1500.0,
  "applied_coupon": "ABFRL20",
  "loyalty_points_used": 50
}
```

### Check User Points
```bash
GET /loyalty/points/user123
```

## Running

```bash
cd backend/agents/worker_agents/loyalty
python app.py
```

Server: `http://localhost:8002`
