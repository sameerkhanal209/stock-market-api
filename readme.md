
# Distributed Stock Market Watchlist & Analytics API

**Stock Market backend system** built with Django 4.2, Django REST Framework, PostgreSQL, Redis, and Celery.

This project implements **all required features** specified in the task.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/sameerkhanal209/stock-market-api
cd stock-market-api

# Start the full stack
docker-compose up --build -d

# Apply migrations
docker-compose exec web python manage.py migrate

# Create superuser (Admin tier)
docker-compose exec web python manage.py createsuperuser
```

Access:
- Admin panel: http://localhost:8000/admin/
- API root: http://localhost:8000/api/v1/
- OpenAPI schema: http://localhost:8000/openapi.json

## API Documentation (OpenAPI 3.0)

The API is fully documented with OpenAPI 3.0.

- **Interactive Swagger UI**: https://petstore.swagger.io/?url=http://localhost:8000/openapi.json
- **ReDoc (Recommended)**: https://redocly.github.io/redoc/?url=http://localhost:8000/openapi.json
- **Raw schema**: http://localhost:8000/openapi.json

All endpoints, models, authentication (JWT & API Key), and permissions are auto-documented.

## Architecture Overview

```
apps/
├── accounts/          # Custom User, RBAC, JWT, API Key auth
├── stocks/            # Stock master + time-series prices (indexed)
├── watchlists/        # Watchlists, bulk operations, alerts
├── pricing/           # Celery price ingestion (yfinance)
└── notifications/     # In app notifications + webhooks

core/
├── settings.py        # Environment-based config (dev/Docker)
├── urls.py            # Versioned /api/v1/ routing
└── celery.py          # Celery app instance
```
Docker services:
- web (Django)
- db (PostgreSQL 15)
- redis
- celery_worker
- celery_beat (periodic tasks)


## Key Features Implemented

- **Authentication**
  - JWT with access + refresh tokens, rotation, and blacklisting
  - API Key authentication for internal services (revocable)

- **Authorization (RBAC)**
  - Custom User model with tiers: Admin / Premium / Standard
  - Admin-only: stock master data management, user creation/listing
  - Premium/Admin: multiple watchlists, historical data >30 days
  - Standard: limited (1 watchlist, 30-day history, rate-limited)

- **Stock & Market Data**
  - Separate `Stock` (master) and `StockPrice` (time-series) models
  - Immutable historical prices
  - Endpoints: latest price (cached), historical (date range + tier limit), aggregates (min/max/avg/volatility)

- **Watchlists**
  - Multiple per user (tier-restricted)
  - Bulk add/remove stocks
  - Duplicate prevention (`unique_together`)
  - Optimized queries (prefetch_related to avoid N+1)
  - JSON field for alert thresholds

- **Alerts & Notifications (Advanced)**
  - Price alerts (above/below threshold)
  - Event-driven via Django signals on price save
  - In-app notification model
  - Webhook delivery (fire-and-forget)

- **External Integrations**
  - Real-time price ingestion using **yfinance** (free, reliable)
  - Periodic Celery beat task (every 5 minutes)
  - Idempotent updates, graceful fallback, rate-friendly

- **Performance & Scalability**
  - Composite index `(stock, -timestamp)` for fast latest/range queries
  - Redis caching of latest prices with invalidation
  - Cursor-based pagination
  - Custom querysets/managers
  - Load-safe design (no expensive sync operations)

- **Observability & Reliability**
  - Structured logging ready
  - Health checks via Docker
  - Centralized error handling

## Design Decisions & Trade-offs

- **Apps in `apps/` directory** → Clean, scalable structure
- **Custom User model with tier field** → Simple, performant RBAC without extra tables
- **Redis for both cache and Celery broker** → Simplicity; easy to split later
- **Cursor pagination** → Scalable for large datasets

## Scaling Considerations

- Horizontal Celery workers for ingestion
- Redis clustering for high-traffic caching
- Future partitioning on `StockPrice.timestamp`
- Rate limiting per tier using DRF throttling

## Security Considerations

- JWT rotation + blacklisting
- API Key revocation via `is_active`
- Tier-based permission classes
- Password hashing with PBKDF2
- Input validation via serializers
- No sensitive data exposure

## Performance Optimizations

- Critical indexes on symbol, tier, stock+timestamp
- Custom querysets for aggregates (computed in DB)
- Redis latest price caching with invalidation
- Prefetch_related in watchlist listing
- Atomic bulk operations


Thank you for the opportunity!
