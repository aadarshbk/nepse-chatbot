# app.py
"""
NEPSE Expert Chatbot - Main Flask Application
Integrates Groq AI, NEPSE Data, and Session Management
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from ai_service import ai_service
from nepse_data import nepse_fetcher
from utils import extract_stock_symbol
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Flask App
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_key_change_in_prod")
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Set True in production with HTTPS
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # Session expires in 1 hour

# =============================================================================
# Helper Functions
# =============================================================================

def get_chat_history():
    """Retrieve chat history from session"""
    if 'chat_history' not in session:
        session['chat_history'] = []
    return session['chat_history']

def add_to_history(role, message):
    """Add message to session history"""
    history = get_chat_history()
    history.append({
        "role": role, 
        "content": message,
        "timestamp": datetime.now().isoformat()
    })
    session['chat_history'] = history
    session.modified = True

def clear_chat_history():
    """Clear chat history from session"""
    session['chat_history'] = []
    session.modified = True

def format_chat_for_template(history):
    """Format chat history for HTML template (list of tuples)"""
    chat_list = []
    for msg in history:
        sender = "You" if msg['role'] == 'user' else "NepseBot"
        chat_list.append((sender, msg['content']))
    return chat_list

def build_market_context(message):
    """
    Build market context based on user query.
    Checks for stock symbols and price-related keywords.
    """
    context = ""
    message_lower = message.lower()
    
    # Check for specific stock symbol
    symbol = extract_stock_symbol(message)
    
    if symbol:
        price_data = nepse_fetcher.get_live_price(symbol)
        context += f"\n[STOCK DATA]: User is asking about {symbol}. Live Data: {price_data}"
    
    # Check for general price queries
    elif any(word in message_lower for word in ['price', 'ltp', 'rate', 'buy', 'sell', 'value']):
        context += "\n[PRICE QUERY]: User is asking about stock prices generally."
    
    # Check for market status
    if any(word in message_lower for word in ['market', 'open', 'close', 'holiday']):
        status = nepse_fetcher.get_market_status()
        context += f"\n[MARKET STATUS]: {status}"
    
    # Check for index query
    if 'index' in message_lower or 'nepse' in message_lower:
        index = nepse_fetcher.get_nepse_index()
        if index:
            context += f"\n[NEPSE INDEX]: {index}"
    
    return context

# =============================================================================
# Routes
# =============================================================================

@app.route('/')
def index():
    """
    Main landing page.
    Displays chat interface with market snapshot sidebar.
    """
    # Get market data for sidebar
    summary = nepse_fetcher.get_market_summary()
    trend = nepse_fetcher.get_market_trend()
    
    # Get chat history
    history = get_chat_history()
    
    # Format for template
    chat_list = format_chat_for_template(history)
    
    return render_template(
        'index.html',
        bot_name="NepseBot",
        summary=summary,
        trend=trend,
        chat=chat_list
    )

@app.route('/chat', methods=['POST'])
def chat():
    """
    Handle chat messages.
    Supports both regular form submission and AJAX requests.
    """
    user_message = request.form.get('message')
    
    # Validate input
    if not user_message or not user_message.strip():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'reply': 'Please enter a message.', 'error': True})
        return redirect(url_for('index'))
    
    user_message = user_message.strip()
    
    # Check for special commands
    if user_message.lower() in ['/clear', '/reset', 'clear chat']:
        clear_chat_history()
        bot_response = "Chat history cleared. How can I help you with NEPSE today?"
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'reply': bot_response, 'cleared': True})
        return redirect(url_for('index'))
    
    # 1. Add user message to history
    add_to_history('user', user_message)
    
    # 2. Build market context from tools
    market_context = build_market_context(user_message)
    
    # 3. Get AI Response
    history = get_chat_history()
    # Convert session history to format AI expects (exclude current user msg)
    ai_history = [
        {"role": msg['role'], "content": msg['content']} 
        for msg in history[:-1]
    ]
    
    bot_response = ai_service.chat(
        message=user_message,
        history=ai_history,
        market_context=market_context
    )
    
    # 4. Add bot response to history
    add_to_history('assistant', bot_response)
    
    # 5. Return response based on request type
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # AJAX request - return JSON
        return jsonify({
            'reply': bot_response,
            'error': False,
            'context': market_context if market_context else None
        })
    else:
        # Regular form submission - redirect
        return redirect(url_for('index'))

@app.route('/api/market')
def api_market():
    """
    API endpoint for market data.
    Can be used by frontend for real-time updates.
    """
    return jsonify({
        'summary': nepse_fetcher.get_market_summary(),
        'trend': nepse_fetcher.get_market_trend(),
        'index': nepse_fetcher.get_nepse_index(),
        'status': nepse_fetcher.get_market_status()
    })

@app.route('/api/stock/<symbol>')
def api_stock(symbol):
    """
    API endpoint for individual stock data.
    Example: /api/stock/NABIL
    """
    price_data = nepse_fetcher.get_live_price(symbol.upper())
    return jsonify(price_data)

@app.route('/clear', methods=['POST'])
def clear_chat():
    """
    Clear chat history endpoint.
    """
    clear_chat_history()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': 'Chat cleared'})
    return redirect(url_for('index'))

# =============================================================================
# Error Handlers
# =============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'error': 'Page not found'}), 404
    return render_template('index.html', 
                          bot_name="NepseBot",
                          summary=None,
                          trend="N/A",
                          chat=[("NepseBot", "Error: Page not found")]), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'error': 'Server error. Please try again.'}), 500
    return render_template('index.html',
                          bot_name="NepseBot",
                          summary=None,
                          trend="N/A",
                          chat=[("NepseBot", "Error: Server error. Please refresh the page.")]), 500

# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == '__main__':
    # Print startup info
    print("=" * 50)
    print("🚀 NEPSE Expert Chatbot Starting...")
    print("=" * 50)
    print(f"📍 Running on: http://127.0.0.1:5000")
    print(f"🧠 AI Service: Groq (Llama3-70b)")
    print(f"📈 Data Source: NEPSE Market Data")
    print("=" * 50)
    
    # Run the app
    app.run(
        debug=True,
        port=5000,
        host='127.0.0.1'
    )