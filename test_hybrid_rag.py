"""Test hybrid RAG implementation."""
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_hybrid_rag():
    """Test hybrid RAG service."""
    print("\n" + "="*60)
    print("Testing Hybrid RAG Implementation")
    print("="*60 + "\n")
    
    try:
        # Import services
        from app.services.hybrid_rag_service import get_hybrid_rag_service
        from app.services.rag_optimizer import get_optimizer
        
        print("✓ Imports successful")
        
        # Get services
        rag_service = get_hybrid_rag_service()
        optimizer = get_optimizer()
        
        print("✓ Services initialized\n")
        
        # Test queries
        test_queries = [
            "What are the trading hours?",
            "How much tax do I pay on dividends?",
            "Explain capital gains tax",
            "What is RSI?",
            "How does settlement work?",
        ]
        
        for query in test_queries:
            print(f"\n{'─'*60}")
            print(f"Query: {query}")
            print(f"{'─'*60}")
            
            try:
                # Retrieve results
                results = rag_service.retrieve(query, top_k=3, optimize=True)
                
                print(f"Found {len(results)} results:\n")
                for i, result in enumerate(results, 1):
                    print(f"{i}. {result.get('title', 'N/A')}")
                    print(f"   Score: {result.get('score', 0):.3f}")
                    print(f"   Dense: {result.get('dense_score', 0):.3f} | "
                          f"Sparse: {result.get('sparse_score', 0):.3f}")
                    print()
                    
            except Exception as e:
                print(f"✗ Error retrieving results: {e}")
        
        print(f"\n{'='*60}")
        print("Test Complete!")
        print(f"{'='*60}\n")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chat_integration():
    """Test chat service integration with hybrid RAG."""
    print("\n" + "="*60)
    print("Testing Chat Service Integration")
    print("="*60 + "\n")
    
    try:
        from app.services.chat_service import generate_bot_reply
        from app.core import settings
        
        print("✓ Chat service imported\n")
        
        # Test query
        test_message = "What's the capital gains tax on NABIL shares if I sell after 6 months?"
        
        print(f"Test Message: {test_message}\n")
        
        response = generate_bot_reply(message=test_message, symbol="NABIL")
        
        print("Chat Response:")
        print(f"  Bot: {response.get('bot_name')}")
        print(f"  Symbol: {response.get('symbol')}")
        print(f"  Reasoning:\n    {response.get('reasoning')}\n")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_hybrid_rag()
    if success:
        success = test_chat_integration()
    
    sys.exit(0 if success else 1)
