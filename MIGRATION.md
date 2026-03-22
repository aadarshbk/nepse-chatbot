# Migration & Clean-up Guide

This guide helps you finalize the migration from the old flat structure to the new organized app package structure.

## Current State

The project now has both:
- ✅ **New organized structure** in `app/` package
- ⚠️  **Old files** at root level (for backward compatibility)

## Step 1: Test the New Structure

Before removing old files, verify everything works:

```bash
# Install dependencies (if not done)
pip install -r requirements.txt

# Test the new structure locally
uvicorn app.main:app --reload

# Visit http://localhost:8000 and verify the chatbot works
```

## Step 2: Run Tests

```bash
pytest tests/ -v
```

If tests pass, you're ready for cleanup.

## Step 3: Clean Up Old Files (Optional)

The following files have been migrated and can be safely deleted:

### Root-level Python files to remove:
```bash
rm app.py                    # Migrated to: app/main.py, app/api/chat.py
rm nepse_data.py             # Migrated to: app/services/nepse_service.py
rm chat_service.py           # Migrated to: app/services/chat_service.py
rm ai_service.py             # Migrated to: app/services/ai_service.py
rm analysis.py               # Migrated to: app/services/analysis_service.py
rm knowledge_base.py         # Migrated to: app/services/knowledge_service.py
rm utils.py                  # Migrated to: app/utils/helpers.py
```

**Or use git to remove:**
```bash
git rm app.py nepse_data.py chat_service.py ai_service.py analysis.py knowledge_base.py utils.py
git commit -m "Remove old root-level Python files, migrated to app/ package"
```

## Step 4: Verify After Cleanup

```bash
# Test again after cleanup
uvicorn app.main:app --reload

# Run tests again
pytest tests/ -v

# Try building Docker image
docker build -t tradmind-chatbot .
docker run -e GROQ_API_KEY=test_key -p 8000:8000 tradmind-chatbot
```

## Step 5: Deploy to Render

With the cleanup complete, deploy to Render:

1. Push to GitHub:
```bash
git push origin main
```

2. Render automatically detects `render.yaml` and deploys
3. Verify deployment by visiting your Render URL

## File Migration Map

For reference, here's where each file moved:

| Old File | New Location | New Path |
|----------|-------------|----------|
| `app.py` | Main app + Routes | `app/main.py` + `app/api/chat.py` |
| `nepse_data.py` | NEPSE Service | `app/services/nepse_service.py` |
| `chat_service.py` | Chat Service | `app/services/chat_service.py` |
| `ai_service.py` | AI Service | `app/services/ai_service.py` |
| `analysis.py` | Analysis Service | `app/services/analysis_service.py` |
| `knowledge_base.py` | Knowledge Service | `app/services/knowledge_service.py` |
| `utils.py` | Utils Helpers | `app/utils/helpers.py` |

## Import Changes

If you have any custom code, update imports:

**Old imports:**
```python
from app import get_session
from chat_service import generate_bot_reply
from utils import extract_stock_symbol
```

**New imports:**
```python
from app.api.chat import get_session
from app.services import generate_bot_reply
from app.utils import extract_stock_symbol
```

## Troubleshooting

### Import errors after cleanup?
- Ensure you're creating a proper `.env` file from `.env.example`
- Verify `GROQ_API_KEY` is set
- Check that you have the right Python version (3.10+)

### Tests failing?
- Run `pip install -r requirements.txt` again
- Make sure `pytest` is installed: `pip install pytest pytest-asyncio`
- Check that all services can import correctly

### Docker build fails?
- Verify Dockerfile references `app.main:app` (should be updated already)
- Run `docker build --no-cache -t tradmind-chatbot .` to rebuild

## Keeping Old Files (Alternative)

If you want to keep old files as reference initially:

```bash
# Create an 'archive' directory
mkdir archive_old_files
mv app.py analysis.py chat_service.py nepse_data.py knowledge_base.py ai_service.py utils.py archive_old_files/

# Later, when confident, delete the archive
rm -rf archive_old_files
```

## Verification Checklist

- [ ] New structure works locally (`uvicorn app.main:app --reload`)
- [ ] Tests pass (`pytest tests/ -v`)
- [ ] Old files removed or archived
- [ ] Docker build successful (`docker build -t tradmind-chatbot .`)
- [ ] Docker runs correctly (`docker run -p 8000:8000 ...`)
- [ ] `.env` file configured with `GROQ_API_KEY`
- [ ] `render.yaml` is correct (updated already)
- [ ] Ready to push to GitHub and deploy to Render

## Questions?

Refer to:
- [STRUCTURE.md](STRUCTURE.md) - Architecture and organization
- [README.md](README.md) - Setup and deployment
- Individual files for implementation details

Good luck with your deployment! 🚀
