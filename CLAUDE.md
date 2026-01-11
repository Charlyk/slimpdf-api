# SlimPDF Backend - Claude Code Instructions

## Overview

This is the **SlimPDF** backend API, a server-side PDF processing service built with Python and FastAPI. It provides compression, merging, and image-to-PDF conversion with Ghostscript-powered processing.

**Domain:** slimpdf.io
**Stack:** Python 3.11+, FastAPI, PostgreSQL (Railway), Ghostscript
**Frontend:** Separate Next.js repo (Vercel)

---

## CRITICAL: Use Beads for Task Management

**STOP using markdown files for TODO lists. Use Beads (`bd`) instead.**

### What is Beads?

Beads is a git-backed issue tracker designed for AI coding agents. It provides:

- Persistent memory across sessions
- Dependency tracking between tasks
- Ready work detection (tasks with no blockers)
- Automatic sync via git

### First Steps Every Session

```bash
# 1. Check beads health
bd doctor

# 2. See what's ready to work on
bd ready --json

# 3. Review current task list
bd list --status open
```

### Creating Issues

```bash
# Create a task
bd create "Implement PDF compression endpoint" -t task -p 1

# Create a bug
bd create "Fix file cleanup on error" -t bug -p 0

# Create an epic for larger features
bd create "User authentication system" -t epic -p 1

# Create with description
bd create "Add rate limiting" -t task -p 2 -d "Implement rate limiting for API endpoints to prevent abuse"

# Create with labels
bd create "Optimize Ghostscript settings" -t task -p 2 -l performance,compression
```

### Managing Dependencies

```bash
# Task B depends on Task A (B is blocked by A)
bd dep add <task-b-id> <task-a-id> --type blocks

# Mark related tasks
bd dep add <task-id> <related-id> --type related

# When you discover new work while working on something
bd create "Found edge case in compression" -t bug -p 1
bd dep add <new-bug-id> <current-task-id> --type discovered-from

# View dependency tree
bd dep tree <epic-id>
```

### Working on Tasks

```bash
# Start working on a task
bd update <task-id> --status in_progress

# Add notes as you work
bd update <task-id> --notes "Implemented basic endpoint, need to add validation"

# Close completed task
bd close <task-id> --reason "Implemented and tested"

# Close multiple tasks
bd close <id1> <id2> <id3> --reason "Batch implementation complete"
```

### Finding Work

```bash
# Show tasks ready to work on (no blockers)
bd ready
bd ready --json
bd ready --priority 1  # Only high priority

# Show blocked tasks
bd blocked

# Filter by type
bd list --type bug
bd list --type task --status open

# Search
bd list --title-contains "compression"
```

### Session End Protocol

Before ending any session, complete these steps:

```bash
# 1. File issues for any discovered work
bd create "TODO item found during work" -t task -p 2

# 2. Update in-progress tasks
bd update <task-id> --notes "Progress: completed X, remaining Y"

# 3. Close completed tasks
bd close <task-id> --reason "Completed"

# 4. Sync the database
bd sync

# 5. Commit and push
git add .beads/
git commit -m "Update beads issues"
git push

# 6. Verify clean state
git status
bd ready --json  # Show next recommended work
```

---

## Project Structure

```
slimpdf-api/
├── app/
│   ├── main.py              # FastAPI application entry
│   ├── config.py            # Settings and environment variables
│   ├── database.py          # PostgreSQL connection
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── subscription.py
│   │   ├── api_key.py
│   │   ├── job.py
│   │   └── usage_log.py
│   ├── routers/             # API endpoints
│   │   ├── compress.py
│   │   ├── merge.py
│   │   ├── image_to_pdf.py
│   │   ├── auth.py
│   │   └── billing.py
│   ├── services/            # Business logic
│   │   ├── compression.py   # Ghostscript wrapper
│   │   ├── merge.py         # PyMuPDF merge logic
│   │   ├── image_convert.py # Pillow + img2pdf
│   │   └── file_manager.py  # Temp file handling
│   ├── middleware/          # Auth, rate limiting
│   └── utils/               # Helpers
├── tests/
├── migrations/              # Alembic migrations
├── Dockerfile
├── requirements.txt
├── .beads/                  # Beads issue tracker (git-synced)
└── CLAUDE.md                # This file
```

---

## Development Guidelines

### Code Style

- Use **type hints** everywhere
- Follow **PEP 8** conventions
- Use **async/await** for I/O operations
- Document functions with docstrings

```python
async def compress_pdf(
    file_path: Path,
    quality: CompressionQuality,
    target_size_mb: float | None = None
) -> CompressionResult:
    """
    Compress a PDF file using Ghostscript.
    
    Args:
        file_path: Path to input PDF
        quality: Compression quality preset
        target_size_mb: Optional target file size in MB
        
    Returns:
        CompressionResult with output path and statistics
        
    Raises:
        CompressionError: If Ghostscript fails
    """
    ...
```

### Error Handling

Always use specific exception types:

```python
from app.exceptions import (
    FileProcessingError,
    FileSizeLimitError,
    RateLimitError,
    AuthenticationError,
)

try:
    result = await compress_pdf(file_path, quality)
except subprocess.CalledProcessError as e:
    raise FileProcessingError(f"Ghostscript failed: {e.stderr}")
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_compression.py

# Run specific test
pytest tests/test_compression.py::test_compress_basic -v
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Add usage_logs table"

# Run migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1
```

---

## Git Workflow

### Branch Structure

- **main**: Production branch, never commit directly
- **develop**: Primary development branch
- **feature/***: Feature branches from develop
- **fix/***: Bug fix branches from develop

### Workflow

```bash
# Start new feature
git checkout develop
git pull origin develop
git checkout -b feature/add-compression-endpoint

# Create beads issue for tracking
bd create "Add PDF compression endpoint" -t feature -p 1

# Work on feature, commit regularly
git add .
git commit -m "feat: add compression endpoint (bd-abc)"

# When complete, merge to develop
git checkout develop
git merge feature/add-compression-endpoint
git push origin develop

# Close the beads issue
bd close bd-abc --reason "Merged to develop"
```

### Commit Message Format

Include beads issue ID in commit messages:

```
feat: add PDF compression endpoint (bd-abc)
fix: handle empty file uploads (bd-xyz)
docs: update API documentation (bd-123)
refactor: extract file handling logic (bd-456)
test: add compression unit tests (bd-789)
```

---

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/slimpdf

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://slimpdf.io

# Stripe
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# Email
RESEND_API_KEY=re_xxx

# File Processing
TEMP_FILE_DIR=/tmp/slimpdf
FILE_EXPIRY_FREE_HOURS=1
FILE_EXPIRY_PRO_HOURS=24
MAX_FILE_SIZE_FREE_MB=20
MAX_FILE_SIZE_PRO_MB=100

# Rate Limiting
RATE_LIMIT_FREE_PER_DAY=2
RATE_LIMIT_PRO_PER_DAY=0  # 0 = unlimited
```

---

## Common Tasks

### Adding a New Endpoint

1. Create beads issue: `bd create "Add new endpoint" -t task -p 2`
2. Create router in `app/routers/`
3. Add service logic in `app/services/`
4. Write tests in `tests/`
5. Update API documentation
6. Close issue: `bd close <id> --reason "Implemented"`

### Adding a Database Table

1. Create beads issue for tracking
2. Add model in `app/models/`
3. Create migration: `alembic revision --autogenerate -m "Add table_name"`
4. Run migration: `alembic upgrade head`
5. Close issue

### Debugging Ghostscript

```bash
# Test Ghostscript directly
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
   -dNOPAUSE -dQUIET -dBATCH -sOutputFile=output.pdf input.pdf

# Check Ghostscript version
gs --version

# List available devices
gs -h | grep -A 100 "Available devices"
```

---

## API Quick Reference

### Compression

```bash
POST /api/v1/compress
Content-Type: multipart/form-data

file: <PDF file>
quality: low|medium|high|custom
target_size_mb: <optional float>
```

### Merge

```bash
POST /api/v1/merge
Content-Type: multipart/form-data

files: <multiple PDF files>
```

### Image to PDF

```bash
POST /api/v1/image-to-pdf
Content-Type: multipart/form-data

files: <multiple image files>
page_size: a4|letter|original
```

### Check Job Status

```bash
GET /api/v1/status/{job_id}
Authorization: Bearer <api_key>  # Required for API users
```

### Download Result

```bash
GET /api/v1/download/{job_id}
```

---

## Beads Quick Reference

| Command | Description |
|---------|-------------|
| `bd ready` | Show tasks ready to work on |
| `bd list` | List all issues |
| `bd create "Title" -t task -p 1` | Create task with priority 1 |
| `bd show <id>` | Show issue details |
| `bd update <id> --status in_progress` | Start working |
| `bd close <id> --reason "Done"` | Complete task |
| `bd dep add <child> <parent>` | Add dependency |
| `bd dep tree <id>` | View dependency tree |
| `bd stats` | Show project statistics |
| `bd sync` | Sync database with git |

### Priority Levels

- **P0**: Critical, do immediately
- **P1**: High priority
- **P2**: Normal (default)
- **P3**: Low priority
- **P4**: Backlog

### Issue Types

- **epic**: Large feature or initiative
- **feature**: New functionality
- **task**: General work item
- **bug**: Something broken
- **chore**: Maintenance work

---

## Remember

1. **Always use beads** for task tracking, never markdown TODOs
2. **Create issues as you discover work** - don't let things slip
3. **Link dependencies** - helps track what blocks what
4. **Sync before ending sessions** - `bd sync && git push`
5. **Include issue IDs in commits** - enables audit trail
6. **File P0 issues for broken builds** - never leave main broken

---

## Resources

- **PRD:** See SlimPDF_PRD.md for full product requirements
- **Beads Documentation:** https://github.com/steveyegge/beads
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Ghostscript Manual:** https://ghostscript.com/doc/current/Use.htm
- **PyMuPDF Docs:** https://pymupdf.readthedocs.io/

---

*Last updated: January 11, 2026*
