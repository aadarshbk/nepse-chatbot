# TradeMind NEPSE Chatbot

A FastAPI-based educational chatbot for NEPSE (Nepal Stock Exchange) data and trading insights. Built with modern Python packaging patterns and ready for production deployment.

## ✨ Features

- 💬 Interactive chat interface for NEPSE questions
- 📊 Technical analysis (RSI, SMA, trends)
- 📚 Educational knowledge base on NEPSE mechanics
- 🤖 AI-powered responses using Groq API
- 🏠 Clean, organized project structure
- 🐳 Docker support with health checks
- 📦 Modern Python packaging with pyproject.toml
- ✅ Render-ready deployment configuration

## 📁 Project Structure

See [STRUCTURE.md](STRUCTURE.md) for detailed information about the reorganized project structure, which includes:

- `app/` - Main application package with organized modules
- `app/api/` - API routes and endpoints
- `app/services/` - Business logic (chat, AI, analysis, knowledge)
- `app/models/` - Pydantic data schemas
- `app/utils/` - Helper functions
- `app/core/` - Configuration management
- `tests/` - Test suite
- `static/` & `templates/` - Web assets

## 🚀 Quick Start

### Local Development

1. Clone and navigate to project:
```bash
cd chatbot
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

Visit http://localhost:8000 to see the chatbot!

### Using Docker Locally

```bash
# Build image
docker build -t tradmind-chatbot .

# Run container
docker run -e GROQ_API_KEY=your_groq_api_key \
           -e FLASK_SECRET_KEY=your_secret_key \
           -p 8000:8000 \
           tradmind-chatbot

# Or with docker-compose
docker-compose up
```

## 📋 Environment Configuration

Create a `.env` file based on `.env.example`:

```env
# AI Service
GROQ_API_KEY=your_groq_api_key_here

# Security
FLASK_SECRET_KEY=your-secret-key-change-in-production

# App Settings
DEBUG=False
PORT=8000
API_HOST=0.0.0.0
```

Get your Groq API key from: https://console.groq.com

## 🌐 Production Deployment

### Render Deployment

1. Push code to GitHub
2. Create a new **Web Service** on Render
3. Connect your GitHub repository
4. Render automatically detects `render.yaml` configuration
5. Set environment variables in Render dashboard:
   - `GROQ_API_KEY`: Your Groq API key
   - `FLASK_SECRET_KEY`: A secure random string
6. Deploy!

The application will be available at your Render URL.

### Using Docker

```bash
# Build production image
docker build -t tradmind-chatbot:latest .

# Push to registry (Docker Hub, etc.)
docker push your-registry/tradmind-chatbot:latest
```

### Manual Deployment

For production, use a WSGI server like Gunicorn with Uvicorn workers:

```bash
pip install gunicorn
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🧪 Testing

Run the test suite:

```bash
pytest                    # Run all tests
pytest -v               # Verbose output
pytest tests/test_chat.py  # Specific test file
```

## 📚 API Endpoints

- `GET /` - Home page with chat interface
- `POST /chat` - Submit message via HTML form
- `POST /api/chat` - Submit message via JSON API
- `GET /api/market` - Get market data
- `DELETE /api/chat/history` - Clear chat history

## 🏗️ Architecture

The application follows a clean architecture pattern:

```
HTTP Request → API Routes → Services → Configuration
                (api/)      (services/) (core/)
```

Each layer has clear responsibilities:
- **API**: HTTP handling, routing, session management
- **Services**: Business logic, external API calls
- **Core**: Configuration, constants

See [STRUCTURE.md](STRUCTURE.md) for complete architecture details.

## 🔧 Development Workflow

### Adding a New Feature

1. **New Service Logic**: Add to `app/services/`
2. **New API Endpoint**: Add to `app/api/chat.py`
3. **New Data Model**: Add to `app/models/schemas.py`
4. **Tests**: Add to `tests/`

Example:
```python
# app/services/my_new_feature.py
def my_function():
    pass

# app/api/chat.py
@router.get("/api/my-endpoint")
async def my_endpoint():
    return my_function()
```

### Code Style

- Python 3.10+
- Type hints recommended
- Format with Black: `black .`
- Lint with Ruff: `ruff check .`

## 📦 Dependencies

Key packages:
- **FastAPI** - Web framework
- **Groq** - AI API integration
- **LangChain** - NLP utilities
- **Pandas** - Data analysis
- **Pydantic** - Data validation
- **ChromaDB** - Vector store

See `requirements.txt` for complete list.

## 🔒 Security

- Non-root Docker user for container security
- Environment variables for secrets
- Input sanitization
- HTTPS ready for production

## 📄 License

MIT

## 🤝 Contributing

1. Create a feature branch
2. Make changes
3. Add tests
4. Submit pull request

## 📞 Support

For issues or questions:
1. Check [STRUCTURE.md](STRUCTURE.md) for architecture details
2. Review test examples in `tests/`
3. Check environment configuration in `.env.example`

## 🎯 Roadmap

- [ ] Persistent chat history with database
- [ ] User authentication
- [ ] Advanced technical analysis
- [ ] Real-time market data integration
- [ ] Multi-language support
- [ ] API rate limiting
pip install gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Variables

Make sure to set the following environment variables in production:
- `GROQ_API_KEY`: Your Groq API key
- `FLASK_SECRET_KEY`: A secret key for session management

## API Endpoints

- `GET /`: Home page
- `POST /chat`: Chat endpoint (form data)
- `POST /api/chat`: Chat API (JSON)
- `GET /api/market`: Market data API
- `DELETE /api/chat/history`: Clear chat history