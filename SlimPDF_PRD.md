# SlimPDF - Product Requirements Document

## Overview

**Product Name:** SlimPDF
**Domain:** slimpdf.io
**Tagline:** Fast PDF Tools That Just Work
**Launch Target:** 2-3 weeks from start

SlimPDF is a server-side PDF toolkit offering compression, merging, and image-to-PDF conversion. Free tier with daily limits, Pro tier ($9/month or $49/year) unlocks unlimited usage, larger files, batch processing, and API access.

---

## Problem Statement

Browser-based PDF tools (like QuickTools.one) have inherent limitations:

- **Compression:** Client-side JavaScript cannot match Ghostscript compression quality (20-40% vs 60-90% reduction)
- **Large files:** Browsers crash on 50MB+ files
- **Target size:** Cannot reliably compress to exact file size
- **API access:** Not possible with client-only processing

Users with professional needs (email attachment limits, bulk processing, automation) need server-side processing but want a simple, affordable solution without enterprise pricing.

---

## Target Users

### Primary Users

| Segment | Need | Willingness to Pay |
|---------|------|-------------------|
| Office workers | Compress PDFs for email (<10MB) | Medium |
| Students | Merge lecture notes, compress submissions | Low (free tier) |
| Small businesses | Bulk invoice processing, automation | High |
| Developers | API integration for apps | High |
| Freelancers | Client deliverables, portfolio PDFs | Medium |

### User Journey

1. User searches "compress pdf online" or "merge pdf"
2. Finds SlimPDF via SEO, directories, or QuickTools referral
3. Uses free tier, hits daily limit
4. Upgrades to Pro for unlimited access or API

---

## Product Strategy

### Positioning

- **vs Smallpdf ($12/mo):** Cheaper, simpler, faster
- **vs iLovePDF ($7/mo):** Similar price, better compression, API included
- **vs Free tools:** Better results, no watermarks, no sketchy ads
- **vs QuickTools:** Server-side processing, better compression, Pro features

### Competitive Advantage

1. Superior compression via Ghostscript (server-side)
2. Target exact file size (unique feature)
3. API access included in Pro (competitors charge extra)
4. Privacy-focused (files deleted after processing)
5. Simple, fast UX (no account required for free tier)

---

## Features

### Core Tools

#### 1. Compress PDF

**Free Tier:**
- 2 files per day
- Max 20MB input file
- Standard compression preset
- Download link valid 1 hour

**Pro Tier:**
- Unlimited files
- Max 100MB input file
- Target exact file size (e.g., "compress to under 5MB")
- Quality presets: Low, Medium, High, Custom
- Batch upload (up to 20 files)
- Download as ZIP for batch
- Download link valid 24 hours

**Technical Implementation:**
- Ghostscript for compression
- Quality presets map to Ghostscript settings:
  - Low: /screen (72 dpi)
  - Medium: /ebook (150 dpi)
  - High: /printer (300 dpi)
  - Custom: User-defined dpi
- Iterative compression for target file size

#### 2. Merge PDF

**Free Tier:**
- 3 files per day
- Max 5 PDFs per merge
- Max 10MB per file
- Download link valid 1 hour

**Pro Tier:**
- Unlimited files
- Max 50 PDFs per merge
- Max 50MB per file
- Reorder via drag-and-drop
- Batch merge (multiple merge jobs)
- Download link valid 24 hours

**Technical Implementation:**
- PyMuPDF (fitz) or pikepdf for merging
- Preserve bookmarks and metadata options
- Page range selection (e.g., "pages 1-5 from PDF A, pages 10-15 from PDF B")

#### 3. Image to PDF

**Free Tier:**
- 3 files per day
- Max 10 images per conversion
- Max 5MB per image
- Download link valid 1 hour

**Pro Tier:**
- Unlimited files
- Max 100 images per conversion
- Max 20MB per image
- Page size options (A4, Letter, Original)
- Margin settings
- Image quality settings
- Batch conversion
- Download link valid 24 hours

**Technical Implementation:**
- Pillow for image processing
- img2pdf for lossless conversion
- Support formats: JPG, PNG, WebP, TIFF, BMP, GIF

### API Access (Pro Only)

**Endpoints:**

```
POST /api/v1/compress
POST /api/v1/merge
POST /api/v1/image-to-pdf
GET  /api/v1/status/{job_id}
GET  /api/v1/download/{job_id}
```

**Authentication:**
- API key in header: `Authorization: Bearer {api_key}`
- API keys generated in dashboard
- Rate limit: 100 requests/hour (adjustable)

**Request/Response Format:**

```bash
# Compress PDF
curl -X POST https://api.slimpdf.io/v1/compress \
  -H "Authorization: Bearer sk_live_xxxxx" \
  -F "file=@document.pdf" \
  -F "quality=medium" \
  -F "target_size_mb=5"

# Response
{
  "job_id": "abc123",
  "status": "processing",
  "estimated_time": 5
}

# Check status
GET /api/v1/status/abc123

# Response
{
  "job_id": "abc123",
  "status": "completed",
  "original_size": 15728640,
  "compressed_size": 4821523,
  "reduction_percent": 69.3,
  "download_url": "https://api.slimpdf.io/v1/download/abc123",
  "expires_at": "2026-01-12T10:00:00Z"
}
```

**Webhook Support (Future):**
- POST to user-defined URL when job completes
- Useful for async workflows

### User Accounts

**Free Users:**
- No account required to use tools
- Optional account to track usage history
- Email + password or Google OAuth

**Pro Users:**
- Account required for subscription management
- Dashboard with:
  - Usage statistics
  - Billing history
  - API key management
  - Download history

### Subscription Management

**Pricing:**
- Monthly: $9/month
- Annual: $49/year (save 54%)

**Payment:**
- Stripe Checkout for payments
- Stripe Customer Portal for management
- Automatic renewal
- Cancel anytime

**Trial:**
- No free trial (free tier serves this purpose)
- 7-day money-back guarantee

---

## Technical Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Vercel                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Next.js Frontend                        │    │
│  │  - Landing page                                      │    │
│  │  - Tool interfaces                                   │    │
│  │  - Dashboard                                         │    │
│  │  - Auth UI (Auth.js)                                 │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ API calls
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        Railway                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Python Backend (FastAPI)                │    │
│  │  - /api/v1/compress                                  │    │
│  │  - /api/v1/merge                                     │    │
│  │  - /api/v1/image-to-pdf                              │    │
│  │  - /api/v1/auth/verify                               │    │
│  │  - /api/v1/billing                                   │    │
│  └─────────────────────────────────────────────────────┘    │
│                              │                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              PostgreSQL Database                     │    │
│  │  - users, accounts, sessions (Auth.js)               │    │
│  │  - subscriptions, api_keys                           │    │
│  │  - usage_logs, jobs                                  │    │
│  └─────────────────────────────────────────────────────┘    │
│                              │                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Processing Layer                        │    │
│  │  - Ghostscript (compression)                         │    │
│  │  - PyMuPDF/pikepdf (merge)                           │    │
│  │  - Pillow/img2pdf (image to PDF)                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                              │                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              File Storage (Temp)                     │    │
│  │  - Upload staging                                    │    │
│  │  - Processed files                                   │    │
│  │  - Auto-delete after expiry                          │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Services                         │
│  ┌──────────────────────────┐  ┌──────────────────────────┐ │
│  │         Stripe           │  │         Resend           │ │
│  │  - Payments              │  │  - Transactional emails  │ │
│  │  - Subscriptions         │  │  - Receipts              │ │
│  │  - Webhooks              │  │                          │ │
│  └──────────────────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Tech Stack

**Frontend:**
- Next.js 14+ (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui components
- React Query for API calls

**Backend:**
- Python 3.11+
- FastAPI
- Ghostscript (system binary)
- PyMuPDF (fitz) for PDF manipulation
- Pillow for image processing
- img2pdf for image to PDF conversion
- python-multipart for file uploads

**Database:**
- PostgreSQL (Railway)
- Same network as API for low latency
- Tables: users, accounts, sessions, subscriptions, api_keys, usage_logs, jobs

**File Storage:**
- Railway volume (temporary)
- Files auto-deleted after expiry (1h free, 24h Pro)
- No permanent storage of user files

**Authentication:**
- Auth.js (NextAuth) v5
- Credentials provider (email + password)
- Google OAuth
- Sessions stored in Railway Postgres
- JWT tokens for API access

**Payments:**
- Stripe Checkout
- Stripe Customer Portal
- Stripe Webhooks for subscription events

**Email:**
- Resend for transactional emails
- Welcome email
- Payment receipts
- Usage alerts

**Hosting:**
- Frontend: Vercel
- Backend: Railway (Docker container)
- Database: Railway PostgreSQL

### Database Schema

```sql
-- Auth.js required tables
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT,
  email TEXT UNIQUE,
  email_verified TIMESTAMPTZ,
  image TEXT,
  password_hash TEXT, -- For credentials provider
  plan TEXT DEFAULT 'free' CHECK (plan IN ('free', 'pro')),
  stripe_customer_id TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  type TEXT NOT NULL,
  provider TEXT NOT NULL,
  provider_account_id TEXT NOT NULL,
  refresh_token TEXT,
  access_token TEXT,
  expires_at INTEGER,
  token_type TEXT,
  scope TEXT,
  id_token TEXT,
  session_state TEXT,
  UNIQUE(provider, provider_account_id)
);

CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_token TEXT UNIQUE NOT NULL,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  expires TIMESTAMPTZ NOT NULL
);

CREATE TABLE verification_tokens (
  identifier TEXT NOT NULL,
  token TEXT NOT NULL,
  expires TIMESTAMPTZ NOT NULL,
  PRIMARY KEY(identifier, token)
);

-- Application tables
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  stripe_subscription_id TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('active', 'canceled', 'past_due', 'trialing')),
  plan_interval TEXT NOT NULL CHECK (plan_interval IN ('month', 'year')),
  current_period_start TIMESTAMPTZ,
  current_period_end TIMESTAMPTZ,
  cancel_at_period_end BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- API Keys table
CREATE TABLE api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  key_hash TEXT NOT NULL,
  key_prefix TEXT NOT NULL, -- First 8 chars for display: "sk_live_abc..."
  name TEXT DEFAULT 'Default',
  last_used_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  revoked_at TIMESTAMPTZ
);

-- Usage logs table
CREATE TABLE usage_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  tool TEXT NOT NULL CHECK (tool IN ('compress', 'merge', 'image_to_pdf')),
  input_size_bytes BIGINT,
  output_size_bytes BIGINT,
  file_count INTEGER DEFAULT 1,
  api_request BOOLEAN DEFAULT FALSE,
  ip_address INET,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Jobs table (for async processing and downloads)
CREATE TABLE jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  tool TEXT NOT NULL,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
  input_filename TEXT,
  output_filename TEXT,
  file_path TEXT, -- Path on server
  error_message TEXT,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX idx_usage_logs_user_created ON usage_logs(user_id, created_at);
CREATE INDEX idx_usage_logs_created ON usage_logs(created_at);
CREATE INDEX idx_jobs_user ON jobs(user_id);
CREATE INDEX idx_jobs_expires ON jobs(expires_at);
CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX idx_accounts_user ON accounts(user_id);
CREATE INDEX idx_sessions_user ON sessions(user_id);
```

### File Processing Flow

```
1. User uploads file(s)
   │
   ▼
2. Backend validates:
   - File type (PDF for compress/merge, image for image-to-pdf)
   - File size (within tier limits)
   - User quota (daily limit check)
   │
   ▼
3. File saved to temp storage
   - Generate unique job ID
   - Create job record in database
   │
   ▼
4. Process file:
   - Compress: Ghostscript with quality settings
   - Merge: PyMuPDF combine pages
   - Image to PDF: Pillow + img2pdf
   │
   ▼
5. Save output to temp storage
   - Update job record with output path
   - Set expiry time (1h free, 24h Pro)
   │
   ▼
6. Return download URL
   - Signed URL with expiry
   - Update usage log
   │
   ▼
7. Cleanup (cron job every 15 min)
   - Delete expired files
   - Update job status to expired
```

### Security Considerations

**File Security:**
- Files stored with random UUIDs, not original names
- No directory listing
- Signed download URLs with expiry
- Files deleted after expiry (no permanent storage)
- Max file size enforced server-side

**API Security:**
- API keys hashed in database (bcrypt)
- Rate limiting per API key
- Request logging for abuse detection
- CORS restricted to slimpdf.io

**Payment Security:**
- All payments via Stripe (PCI compliant)
- No card data stored
- Webhook signature verification

**Privacy:**
- No file content analysis
- No file retention after expiry
- Usage logs anonymized after 90 days
- GDPR compliant (data deletion on request)

---

## User Interface

### Pages

#### Landing Page (/)

**Above the fold:**
- Headline: "Compress, Merge & Convert PDFs - Fast & Free"
- Subheadline: "Server-powered PDF tools with up to 90% compression. No watermarks. No signup required."
- Primary CTA: Tool selector (Compress / Merge / Image to PDF)
- Trust badges: "Files deleted after processing", "No account required", "256-bit encryption"

**Below the fold:**
- Feature comparison (Free vs Pro)
- How it works (3 steps)
- Compression quality demo (before/after)
- Pricing section
- FAQ
- Footer

#### Tool Pages (/compress, /merge, /image-to-pdf)

**Layout:**
1. Tool header with description
2. File upload zone (drag & drop)
3. Options panel (quality, settings)
4. Process button
5. Progress indicator
6. Download section
7. Upsell banner (if free tier limit reached)

**States:**
- Empty (waiting for upload)
- Files selected (showing file list)
- Processing (progress bar)
- Complete (download ready)
- Error (with retry option)
- Limit reached (upgrade prompt)

#### Pricing Page (/pricing)

**Content:**
- Plan comparison table
- Feature list with checkmarks
- FAQ about billing
- Money-back guarantee
- Stripe checkout integration

#### Dashboard (/dashboard) - Pro users

**Sections:**
- Usage overview (files processed, storage used)
- Recent activity
- API keys management
- Billing (link to Stripe portal)
- Account settings

#### API Documentation (/docs/api)

**Content:**
- Authentication guide
- Endpoint reference
- Code examples (curl, Python, JavaScript)
- Rate limits
- Error codes

### Design System

**Colors:**
- Primary: Blue (#2563EB)
- Secondary: Slate (#64748B)
- Success: Green (#22C55E)
- Error: Red (#EF4444)
- Background: White/Gray (#F8FAFC)

**Typography:**
- Headings: Inter (bold)
- Body: Inter (regular)
- Code: JetBrains Mono

**Components:**
- Use shadcn/ui as base
- Consistent border radius (8px)
- Subtle shadows
- Clean, minimal aesthetic

---

## Development Roadmap

### Week 1: Core Infrastructure

**Day 1-2: Project Setup**
- [ ] Register slimpdf.io domain
- [ ] Create GitHub repository
- [ ] Set up Next.js frontend (Vercel)
- [ ] Set up FastAPI backend (Railway)
- [ ] Configure PostgreSQL database (Railway)
- [ ] Docker setup for Railway with Ghostscript

**Day 3-4: Authentication**
- [ ] Auth.js (NextAuth) v5 integration
- [ ] Credentials provider (email + password)
- [ ] Password hashing with bcrypt
- [ ] Google OAuth
- [ ] Protected routes
- [ ] Session management

**Day 5-6: Compress PDF Tool**
- [ ] File upload endpoint
- [ ] Ghostscript integration
- [ ] Quality presets
- [ ] Target file size feature
- [ ] Download endpoint
- [ ] Basic UI

**Day 7: Billing Setup**
- [ ] Stripe products/prices setup
- [ ] Checkout integration
- [ ] Webhook handlers
- [ ] Subscription status sync

### Week 2: Features & Polish

**Day 8-9: Merge PDF Tool**
- [ ] Multi-file upload
- [ ] File reordering UI
- [ ] PyMuPDF merge logic
- [ ] Page range selection

**Day 10-11: Image to PDF Tool**
- [ ] Image upload (multi-format)
- [ ] Pillow processing
- [ ] img2pdf conversion
- [ ] Page size options

**Day 12-13: Usage Limits & API**
- [ ] Daily limit tracking
- [ ] Limit enforcement
- [ ] API key generation
- [ ] API endpoints
- [ ] Rate limiting

**Day 14: Dashboard**
- [ ] Usage stats
- [ ] API key management
- [ ] Billing portal link
- [ ] Account settings

### Week 3: Launch Prep

**Day 15-16: Landing Page**
- [ ] Hero section
- [ ] Feature sections
- [ ] Pricing section
- [ ] FAQ
- [ ] SEO metadata

**Day 17-18: Testing & Polish**
- [ ] Error handling
- [ ] Mobile responsiveness
- [ ] Cross-browser testing
- [ ] Performance optimization
- [ ] File cleanup cron job

**Day 19-20: Launch**
- [ ] Privacy policy
- [ ] Terms of service
- [ ] API documentation
- [ ] Soft launch
- [ ] Bug fixes
- [ ] Product Hunt prep

---

## SEO Strategy

### Target Keywords

**Primary (tool pages):**

| Keyword | Volume | Difficulty | Target Page |
|---------|--------|------------|-------------|
| compress pdf | 165,000 | 65 | /compress |
| merge pdf | 201,000 | 60 | /merge |
| image to pdf | 135,000 | 58 | /image-to-pdf |

**Golden Keywords (blog):**

| Keyword | Volume | Difficulty | Article |
|---------|--------|------------|---------|
| compress pdf to 1mb | 8,100 | 38 | How to Compress PDF to Exactly 1MB |
| compress pdf for email | 2,900 | 35 | Compress PDF for Email Attachments |
| reduce pdf size without losing quality | 2,400 | 42 | Guide to PDF Compression Quality |
| merge pdf online free | 6,600 | 45 | Best Free PDF Merge Tools |
| jpg to pdf | 90,500 | 55 | Convert JPG to PDF Guide |

### On-Page SEO

**Each tool page includes:**
- Keyword-optimized title (<65 chars)
- Meta description (130-160 chars)
- H1 with primary keyword
- Feature sections with secondary keywords
- FAQ section (JSON-LD schema)
- HowTo schema
- Internal links to other tools

### Content Strategy

**Launch content:**
1. Landing page with comprehensive SEO copy
2. Tool pages with feature descriptions
3. API documentation

**Post-launch blog articles (1-2 per week):**
- How-to guides targeting long-tail keywords
- Comparison articles (SlimPDF vs competitors)
- Use case guides (compress PDF for email, merge invoices, etc.)

---

## Marketing Plan

### Pre-Launch

- [ ] Set up analytics (Umami or Plausible)
- [ ] Create social accounts
- [ ] Prepare Product Hunt assets
- [ ] Draft launch announcements

### Launch Week

**Day 1:**
- Add banner to QuickTools.one /pdf-compress
- Post on IndieHackers
- Post on r/SideProject
- Submit to directories (10 from hit list)

**Day 2-3:**
- Product Hunt launch
- X/Twitter announcement
- Dev.to technical article

**Day 4-7:**
- Monitor and respond to feedback
- Fix critical bugs
- Continue directory submissions

### Ongoing

**Weekly:**
- 1 blog article targeting golden keywords
- 5 directory submissions
- Monitor rankings and traffic

**Monthly:**
- Review conversion rates
- A/B test pricing page
- Expand feature set based on feedback

### QuickTools Integration

**Placements:**
- Banner on /pdf-compress: "Need better compression? Try SlimPDF Pro - up to 90% reduction"
- Post-compression message: "Got 30% reduction. Want 70%? Try SlimPDF"
- Blog article: "Browser vs Server PDF Compression" linking to SlimPDF

---

## Metrics & Success Criteria

### Launch Goals (First 30 Days)

| Metric | Target |
|--------|--------|
| Visitors | 1,000 |
| Free tool uses | 500 |
| Signups | 50 |
| Paid conversions | 5 |
| MRR | $45 |

### 90-Day Goals

| Metric | Target |
|--------|--------|
| Monthly visitors | 5,000 |
| Monthly tool uses | 2,500 |
| Registered users | 500 |
| Paying customers | 50 |
| MRR | $400-500 |

### 6-Month Goals

| Metric | Target |
|--------|--------|
| Monthly visitors | 20,000 |
| Paying customers | 150 |
| MRR | $1,000+ |

### Key Metrics to Track

- **Acquisition:** Visitors, traffic sources, keyword rankings
- **Activation:** Tool usage rate, signup rate
- **Retention:** Return visits, Pro renewal rate
- **Revenue:** MRR, ARPU, churn rate
- **Referral:** QuickTools to SlimPDF conversion

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Low conversion to Pro | High | High | A/B test pricing, improve free-to-Pro upsells |
| Server costs exceed revenue | Medium | High | Usage-based limits, monitor costs closely |
| Competition undercuts pricing | Medium | Medium | Focus on UX and compression quality |
| Ghostscript processing failures | Low | Medium | Error handling, fallback options, monitoring |
| File storage abuse | Medium | Medium | Strict file size limits, auto-deletion |
| API abuse | Low | Medium | Rate limiting, usage monitoring |

---

## Future Roadmap (Post-Launch)

### Phase 2 (Month 2-3)
- [ ] Additional tools: Split PDF, Rotate PDF, PDF to Image
- [ ] Batch processing improvements
- [ ] Webhook support for API
- [ ] Team/organization accounts

### Phase 3 (Month 4-6)
- [ ] OCR (PDF to searchable text)
- [ ] PDF editing (add text, images)
- [ ] White-label API for businesses
- [ ] Enterprise tier

### Phase 4 (Month 6+)
- [ ] Desktop app (Electron)
- [ ] Mobile apps
- [ ] Browser extension
- [ ] Zapier/Make integrations

---

## Appendix

### Ghostscript Quality Settings

```bash
# Screen quality (72 dpi) - smallest file
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen \
   -dNOPAUSE -dQUIET -dBATCH -sOutputFile=output.pdf input.pdf

# Ebook quality (150 dpi) - balanced
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
   -dNOPAUSE -dQUIET -dBATCH -sOutputFile=output.pdf input.pdf

# Printer quality (300 dpi) - high quality
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/printer \
   -dNOPAUSE -dQUIET -dBATCH -sOutputFile=output.pdf input.pdf

# Prepress quality (300 dpi, color preserving) - highest quality
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/prepress \
   -dNOPAUSE -dQUIET -dBATCH -sOutputFile=output.pdf input.pdf

# Custom DPI
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
   -dDownsampleColorImages=true -dColorImageResolution=120 \
   -dNOPAUSE -dQUIET -dBATCH -sOutputFile=output.pdf input.pdf
```

### Environment Variables

```bash
# Frontend (.env.local)
NEXT_PUBLIC_API_URL=https://api.slimpdf.io
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_xxx

# Auth.js
AUTH_SECRET=xxx # Generate with: openssl rand -base64 32
AUTH_URL=https://slimpdf.io
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx

# Database (shared between frontend Auth.js and backend)
DATABASE_URL=postgresql://user:pass@host:5432/slimpdf

# Backend (.env)
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
RESEND_API_KEY=re_xxx
TEMP_FILE_DIR=/tmp/slimpdf
FILE_EXPIRY_FREE_HOURS=1
FILE_EXPIRY_PRO_HOURS=24
```

### Cost Estimates

| Service | Free Tier | Estimated Cost |
|---------|-----------|----------------|
| Vercel | 100GB bandwidth | $0 initially |
| Railway (API + Postgres) | $5 credit | $5-20/month |
| Stripe | 2.9% + $0.30 | Per transaction |
| Resend | 3,000 emails/month | $0 initially |
| Domain | - | $30-50/year |

**Total estimated monthly cost:** $5-25 initially, scaling with usage.

---

*Document created: January 11, 2026*
*Last updated: January 11, 2026*
*Version: 1.0*
