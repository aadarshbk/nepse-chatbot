# Project Structure Guide

## Directory Organization

```
tradmind-chatbot/
├── app/                           # Main application package
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   │
│   ├── core/                      # Core configuration
│   │   ├── __init__.py
│   │   └── config.py              # Settings and environment config
│   │
│   ├── api/                       # API routes and endpoints
│   │   ├── __init__.py
│   │   └── chat.py                # Chat endpoints, session management
│   │
│   ├── services/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── chat_service.py        # Chat request processing
│   │   ├── ai_service.py          # Groq AI integration
│   │   ├── analysis_service.py    # Market data analysis
│   │   ├── nepse_service.py       # NEPSE data fetching
│   │   └── knowledge_service.py   # Knowledge base management
│   │
│   ├── models/                    # Pydantic data models
│   │   ├── __init__.py
│   │   └── schemas.py             # Request/response schemas
│   │
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       └── helpers.py             # Helper functions and constants
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py                # Pytest configuration and fixtures
│   └── test_chat.py               # Chat API tests
│
├── static/                        # Static web assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
│
├── templates/                     # Jinja2 HTML templates
│   └── index.html
│
├── data/                          # Data directory (CSV files, vectorstore)
│   ├── documents/
│   └── vectorstore/
│
├── config/                        # Configuration files (reserved)
│
├── .env.example                   # Example environment variables
├── pyproject.toml                 # Modern Python packaging
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker containerization
├── docker-compose.yml             # Local development with Docker
├── render.yaml                    # Render deployment config
└── README.md                      # This file
```

## Key Improvements Over Original Structure

### 1. **Organized Module Structure**
- **Before**: All Python files at root level (messy, harder to scale)
- **After**: Organized into logical packages (core, api, services, models, utils)

### 2. **Separation of Concerns**
- **Core**: Configuration and settings management
- **API**: HTTP endpoints and routes
- **Services**: Business logic isolated from HTTP layer
- **Models**: Data validation schemas
- **Utils**: Shared helper functions

### 3. **Easier Testing**
- Services can be tested independently
- API routes can be tested with FastAPI's TestClient
- Configuration is centralized and mockable

### 4. **Better Deployment**
- Pydantic Settings for environment management
- `pyproject.toml` for modern Python packaging
- `.env.example` for documentation
- Docker with security best practices (non-root user, health checks)

### 5. **Scalability**
- Easy to add new endpoints in `/api/`
- Easy to add new services in `/services/`
- Clear structure for adding databases, caching, etc.

## How Dependencies Work

```
HTTP Request
    ↓
API Routes (app/api/chat.py)
    ↓
Services (app/services/)
    ├─→ chat_service.py (orchestrates)
    ├─→ ai_service.py (Groq integration)
    ├─→ analysis_service.py (technical analysis)
    ├─→ knowledge_service.py (NEPSE knowledge)
    └─→ nepse_service.py (market data)
    ↓
Configuration (app/core/config.py)
```

## Running the Application

### Local Development
```bash
pip install -r requirements.txt
cp .env.example .env  # Configure your settings
uvicorn app.main:app --reload
```

### With Docker
```bash
docker build -t tradmind-chatbot .
docker run -e GROQ_API_KEY=your_key -p 8000:8000 tradmind-chatbot
```

### Docker Compose (for development)
```bash
docker-compose up
```

## Environment Configuration

See `.env.example` for all available settings. Key variables:

- `GROQ_API_KEY`: Your Groq API key
- `FLASK_SECRET_KEY`: Secret key for sessions
- `DEBUG`: Enable debug mode (False in production)
- `PORT`: Port to run on (default 8000)

## Render Deployment

1. Push code to GitHub
2. Create Web Service on Render
3. Set environment variables:
   - `GROQ_API_KEY`
   - `FLASK_SECRET_KEY`
4. Render automatically uses `render.yaml` configuration
5. Deploy!

## Adding a New Feature

### Add a new service
1. Create file in `app/services/new_feature.py`
2. Export from `app/services/__init__.py`
3. Use in other services or API routes

### Add a new API endpoint
1. Add function to `app/api/chat.py`
2. Use router decorator: `@router.get()`, `@router.post()`, etc.
3. Already included in `app.main.py`

### Add a new data model
1. Create schema in `app/models/schemas.py`
2. Export from `app/models/__init__.py`
3. Use in API endpoints for validation

## Testing

Run tests:
```bash
pytest
pytest -v              # Verbose
pytest tests/test_chat.py  # Specific test file
```

## Production Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Generate strong `FLASK_SECRET_KEY`
- [ ] Set `GROQ_API_KEY` environment variable
- [ ] Use production database (currently uses in-memory sessions)
- [ ] Configure CORS if needed
- [ ] Set up monitoring/logging
- [ ] Use production ASGI server (Uvicorn with multiple workers or Gunicorn)

## Future Improvements

- [ ] Add database for persistent chat history
- [ ] Add Redis for caching
- [ ] Add authentication/user management
- [ ] Add API rate limiting
- [ ] Add comprehensive logging
- [ ] Add monitoring and error tracking
