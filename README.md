# SlimPDF API

Backend API for [SlimPDF](https://slimpdf.io) - a PDF processing service offering compression, merging, and image-to-PDF conversion.

## Tech Stack

- **Framework:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL with SQLAlchemy (async)
- **PDF Processing:** Ghostscript, PyMuPDF
- **Image Processing:** Pillow, img2pdf
- **Authentication:** JWT + Google OAuth
- **Payments:** Stripe
- **Deployment:** Railway

## Features

- **PDF Compression** - Reduce file sizes with quality presets (low/medium/high) or target size
- **PDF Merge** - Combine multiple PDFs into one
- **Image to PDF** - Convert images (JPG, PNG, WebP, etc.) to PDF
- **User Authentication** - Google OAuth with JWT tokens
- **Subscription Billing** - Stripe integration for Pro tier
- **Rate Limiting** - Daily limits for free tier users
- **API Keys** - Programmatic access for Pro users

## API Endpoints

### PDF Processing

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/compress` | Compress a PDF file |
| POST | `/v1/merge` | Merge multiple PDFs |
| POST | `/v1/image-to-pdf` | Convert images to PDF |
| GET | `/v1/status/{job_id}` | Get job status |
| GET | `/v1/download/{job_id}` | Download processed file |

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/auth/google` | Exchange Google token for JWT |
| GET | `/v1/auth/me` | Get current user info |
| GET | `/v1/auth/verify` | Verify token validity |

### Billing

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/billing/checkout` | Create Stripe checkout session |
| POST | `/v1/billing/portal` | Create Stripe customer portal |
| POST | `/v1/billing/webhook` | Stripe webhook handler |

### API Keys (Pro only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/keys` | List API keys |
| POST | `/v1/keys` | Create new API key |
| DELETE | `/v1/keys/{key_id}` | Revoke API key |

## Local Development

### Prerequisites

- Python 3.11+
- Docker (for PostgreSQL)
- Ghostscript (`brew install ghostscript` on macOS)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/slimpdf-api.git
   cd slimpdf-api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start PostgreSQL**
   ```bash
   docker run -d \
     --name slimpdf-postgres \
     -e POSTGRES_USER=slimpdf \
     -e POSTGRES_PASSWORD=slimpdf \
     -e POSTGRES_DB=slimpdf \
     -p 5432:5432 \
     postgres:16-alpine
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env.local
   ```

   Edit `.env.local` with your settings:
   ```env
   DATABASE_URL=postgresql://slimpdf:slimpdf@localhost:5432/slimpdf
   JWT_SECRET=your-secure-secret-key
   GOOGLE_CLIENT_ID=your-google-client-id
   ```

6. **Run migrations**
   ```bash
   alembic upgrade head
   ```

7. **Start the server**
   ```bash
   uvicorn app.main:app --reload
   ```

   API available at http://localhost:8000

   Docs at http://localhost:8000/docs

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `JWT_SECRET` | Secret key for JWT signing | Required |
| `JWT_EXPIRY_HOURS` | JWT token expiration | `24` |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | Required for auth |
| `STRIPE_SECRET_KEY` | Stripe API secret key | Required for billing |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret | Required for billing |
| `STRIPE_PRICE_MONTHLY` | Stripe price ID for monthly plan | Required for billing |
| `STRIPE_PRICE_YEARLY` | Stripe price ID for yearly plan | Required for billing |
| `TEMP_FILE_DIR` | Directory for temporary files | `/tmp/slimpdf` |
| `FILE_EXPIRY_FREE_HOURS` | File retention for free users | `1` |
| `FILE_EXPIRY_PRO_HOURS` | File retention for Pro users | `24` |
| `MAX_FILE_SIZE_FREE_MB` | Max upload size for free users | `20` |
| `MAX_FILE_SIZE_PRO_MB` | Max upload size for Pro users | `100` |
| `RATE_LIMIT_COMPRESS_FREE` | Daily compress limit (free) | `2` |
| `RATE_LIMIT_MERGE_FREE` | Daily merge limit (free) | `3` |
| `RATE_LIMIT_IMAGE_TO_PDF_FREE` | Daily image-to-pdf limit (free) | `3` |
| `CORS_ORIGINS` | Allowed CORS origins | `["https://slimpdf.io"]` |

## Database

### Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Run migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1
```

### Schema

The database schema is compatible with [Auth.js](https://authjs.dev/) (NextAuth v5):

- `users` - User accounts
- `accounts` - OAuth provider connections
- `sessions` - User sessions
- `verification_tokens` - Email verification
- `subscriptions` - Stripe subscriptions
- `api_keys` - API keys for Pro users
- `jobs` - PDF processing jobs
- `usage_logs` - Usage tracking

## Deployment (Railway)

### Setup

1. **Create a new Railway project**

2. **Add PostgreSQL**
   - Add a PostgreSQL database service
   - Copy the connection string

3. **Add a Volume** (for file storage)
   - Create a volume
   - Mount at `/data`
   - Set `TEMP_FILE_DIR=/data/slimpdf`

4. **Configure environment variables**
   - Add all required environment variables
   - Set `DATABASE_URL` from Railway PostgreSQL

5. **Deploy**
   - Connect your GitHub repository
   - Railway auto-deploys on push

### Stripe Webhook

Configure webhook in Stripe Dashboard:
- **URL:** `https://api.slimpdf.io/v1/billing/webhook`
- **Events:**
  - `checkout.session.completed`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_compression.py -v
```

## Project Structure

```
slimpdf-api/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Settings (pydantic-settings)
│   ├── database.py          # Database connection
│   ├── exceptions.py        # Custom exceptions
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py          # User, Account, Session
│   │   ├── subscription.py  # Subscription
│   │   ├── api_key.py       # ApiKey
│   │   ├── job.py           # Job
│   │   └── usage_log.py     # UsageLog
│   ├── routers/             # API endpoints
│   │   ├── auth.py          # Authentication
│   │   ├── billing.py       # Stripe billing
│   │   ├── compress.py      # PDF compression
│   │   ├── merge.py         # PDF merging
│   │   ├── image_to_pdf.py  # Image conversion
│   │   ├── jobs.py          # Job status/download
│   │   └── api_keys.py      # API key management
│   ├── services/            # Business logic
│   │   ├── compression.py   # Ghostscript wrapper
│   │   ├── merge.py         # PyMuPDF merge
│   │   ├── image_convert.py # Image to PDF
│   │   ├── file_manager.py  # File handling
│   │   ├── usage.py         # Usage tracking
│   │   └── google_auth.py   # Google OAuth
│   ├── middleware/          # Auth middleware
│   │   ├── auth.py          # JWT authentication
│   │   ├── api_key.py       # API key authentication
│   │   └── rate_limit.py    # Rate limiting
│   └── utils/               # Utilities
│       └── background.py    # Background tasks
├── migrations/              # Alembic migrations
├── tests/                   # Test suite
├── Dockerfile
├── requirements.txt
├── alembic.ini
└── README.md
```

## API Usage Examples

### Compress a PDF

```bash
curl -X POST https://api.slimpdf.io/v1/compress \
  -F "file=@document.pdf" \
  -F "quality=medium"
```

### Merge PDFs

```bash
curl -X POST https://api.slimpdf.io/v1/merge \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.pdf"
```

### Convert Images to PDF

```bash
curl -X POST https://api.slimpdf.io/v1/image-to-pdf \
  -F "files=@image1.jpg" \
  -F "files=@image2.png" \
  -F "page_size=a4"
```

### Check Job Status

```bash
curl https://api.slimpdf.io/v1/status/{job_id}
```

### Authenticate with Google

```bash
curl -X POST https://api.slimpdf.io/v1/auth/google \
  -H "Content-Type: application/json" \
  -d '{"id_token": "google-id-token"}'
```

### Authenticated Request

```bash
curl https://api.slimpdf.io/v1/auth/me \
  -H "Authorization: Bearer {jwt_token}"
```

## License

Proprietary - All rights reserved.
