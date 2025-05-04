# 🌟 Webhook Delivery Service
> A robust, scalable, and production-ready webhook processing system

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

## 📌 Overview

Modern applications rely heavily on real-time event notifications. This project delivers a high-performance webhook service that:

- ⚡ Ingests webhooks with millisecond latency
- 🔄 Delivers payloads with exponential backoff retries (up to 5 attempts)
- 🔒 Verifies webhook signatures for security
- 📊 Provides complete visibility into delivery status

Built for e-commerce platforms, payment processors, and SaaS applications needing reliable webhook infrastructure.

## 🔥 Why Webhooks Matter

Webhooks power critical workflows:

- 💳 Payment gateways notifying about transactions
- 🔄 GitHub triggering CI/CD pipelines
- 👥 CRM systems syncing customer data

**Our solution solves:**

| Problem | Solution |
|---------|----------|
| 📮 Lost webhooks | Automatic retries with exponential backoff |
| 👁️ No delivery visibility | Full attempt history logging |
| 🔐 Security risks | Payload signature verification |

## 🏗️ Architecture

### Tech Stack

| Category | Technology | Purpose |
|----------|------------|---------|
| Backend | Python + FastAPI | Blazing fast API endpoints |
| Async | Celery + Redis | Background task processing |
| Database | PostgreSQL (GCP Cloud SQL) | Reliable data persistence |
| Caching | Redis Cloud | Queue management + subscription caching |
| Monitoring | Streamlit Dashboard | Real-time delivery analytics |

## 📸 Screenshots

![Screenshot from 2025-05-04 10-59-58](https://github.com/user-attachments/assets/2c1a5f6e-11c3-43da-9b09-136ce30c382c)
![Screenshot from 2025-05-04 11-00-09](https://github.com/user-attachments/assets/dcd3048e-93e5-44c4-b4b3-261b28111cac)
![Screenshot from 2025-05-04 11-00-52](https://github.com/user-attachments/assets/9f4b6512-56da-40e2-a624-dc4a610d2f45)
![Screenshot from 2025-05-04 11-01-21](https://github.com/user-attachments/assets/6f17532a-69d2-46f4-9c2c-03afedfb1950)
![Screenshot from 2025-05-04 11-05-23](https://github.com/user-attachments/assets/ceb2b39b-1eb6-40e5-9319-5c24c3921357)
![Screenshot from 2025-05-04 11-09-00](https://github.com/user-attachments/assets/054d7cb3-0875-4547-8246-e6f0e83aa81a)
![Screenshot from 2025-05-04 11-09-11](https://github.com/user-attachments/assets/e5fe3785-13ad-444a-b82b-34aba1cd5585)

## 🔄 Workflows

### 1. Webhook Processing
![Webhook Processing](https://github.com/user-attachments/assets/79cb01d0-4327-4b1c-acf6-8be2d5a39fe0)

### 2. Database Schema
![Database Schema](https://github.com/user-attachments/assets/2cbed41e-7d9d-41ab-83f1-26e56ad8cf1a)

### 3. Data Fetching Flow
![Data Fetching Flow](https://github.com/user-attachments/assets/65a10e75-e108-4a58-a687-d423be553094)

### 4. Data Update Flow
![Data Update Flow](https://github.com/user-attachments/assets/6631b681-dd78-47ed-b8e7-914065258486)

### 5. Deployment Architecture
![Deployment Architecture](https://github.com/user-attachments/assets/0c028a0d-139f-46ea-9092-d50a68c92d8e)

## 🏃 Local Setup (1 Minute)
```bash
# 1. Clone repo
git clone https://github.com/your-repo/webhook-delivery-service.git
cd webhook-delivery-service

# 2. Setup env
cp .env.example .env  # Update with your Redis/DB credentials

# 3. Run services
docker-compose up --build  # Starts API + Worker + Redis + DB


```

## 📡 API Documentation

1. Create Subscription
POST - https://segwise-webhook-service.onrender.com/api/v1/subscriptions/
Example:
Input:
```
{
  "target_url": "https://hook.eu2.make.com/oa7dkj27u6dsx5lcnj7siwcldjg4uj1v",
  "secret": "2c6d8d1d-01d5-4898-8188-f3cadfd44163",
  "event_types": ["payment.processed"]
}
```

Output:
```
{
    "target_url": "https://hook.eu2.make.com/oa7dkj27u6dsx5lcnj7siwcldjg4uj1v",
    "event_types": [
        "payment.processed"
    ],
    "id": "e5b40e29-5f9d-4c83-8562-6bd0cd3a4e74",
    "is_active": true,
    "created_at": "2025-05-04T06:04:41.250794Z",
    "updated_at": null
}
```

2. Injest Webhook
POST - https://segwise-webhook-service.onrender.com/api/v1/ingest/{subscription_id}
Example:
Input:
```
{
  "event": "payment.processed",
  "amount": 34567
}
```
Output:
```
{
    "status": "accepted",
    "delivery_id": "b3827820-5992-46c1-9866-16940b53093f",
    "subscription_id": "e5b40e29-5f9d-4c83-8562-6bd0cd3a4e74"
}
```

3. Delivery Logs
GET - https://segwise-webhook-service.onrender.com/api/v1/status/delivery/{delivery_id}
Example
Output:
```
{
    "delivery_id": "b3827820-5992-46c1-9866-16940b53093f",
    "attempts": [
        {
            "attempt_number": 0,
            "status": "queued",
            "status_code": null,
            "timestamp": "2025-05-04T06:05:33.813352"
        }
    ]
}
```


## 🧠 Redis Architecture

1. Queues:
celery: Stores pending delivery tasks

2. Caching:
subscription:{id}: Caches subscription details (TTL: 5m)

Key Commands:

```bash
redis-cli KEYS '*'          # List all keys
redis-cli LLEN celery       # Check queue length
redis-cli FLUSHDB           # Clear all data (dev only)
```

## ☁️ Production Deployment

| Service | Provider | Details |
|---------|----------|---------|
| PostgreSQL | GCP Cloud SQL | Managed database service |
| Redis | Redis Cloud | 30MB Free Tier (Dedicated) |
| Streamlit UI | Streamlit Community Cloud | Analytics dashboard |

<p align="center">
Made with ❤️ by Manoj
</p>

