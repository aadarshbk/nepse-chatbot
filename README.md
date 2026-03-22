# TradeMind NEPSE Chatbot

A FastAPI-based chatbot for NEPSE (Nepal Stock Exchange) data and trading insights.

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables in `.env`:
   ```
   GROQ_API_KEY=your_groq_api_key
   FLASK_SECRET_KEY=your_secret_key
   ```

3. Run the application:
   ```bash
   uvicorn app:app --reload
   ```

## Production Deployment

### Using Docker

1. Build the Docker image:
   ```bash
   docker build -t tradmind-chatbot .
   ```

2. Run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

### Manual Deployment

For production, use a WSGI server like Gunicorn with Uvicorn workers:

```bash
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