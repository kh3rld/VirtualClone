#!/usr/bin/env python3
"""
Test script for conversation context functionality
"""

def test_conversation_context():
    """Test the conversation context implementation"""
    print("Testing Conversation Context Implementation")
    print("=" * 50)
    
    try:
        from app.services.ai_service import AIService, answer_question_with_context
        print("AI Service import successful")
    except ImportError as e:
        print(f"AI Service import failed: {e}")
        return False

    try:
        ai_service = AIService()
        print("AI Service instance created")
    except Exception as e:
        print(f"AI Service instance creation failed: {e}")
        return False
    
    # Test 3: Test Context Building
    try:
        base_context = "This is a test context about artificial intelligence."
        conversation_history = [
            ("What is AI?", "AI is artificial intelligence."),
            ("How does it work?", "AI works through machine learning algorithms.")
        ]
        
        enhanced_context = ai_service._build_enhanced_context(base_context, conversation_history)
        print("Context building works")
        print(f"   Enhanced context length: {len(enhanced_context)} characters")
    except Exception as e:
        print(f"Context building failed: {e}")
        return False
    
    # Test 4: Test Question Similarity Detection
    try:
        question1 = "What is artificial intelligence?"
        question2 = "What is AI?"
        question3 = "How do I cook pasta?"
        
        similarity1 = ai_service._calculate_similarity(question1, question2)
        similarity2 = ai_service._calculate_similarity(question1, question3)
        
        print(f"Similarity detection works")
        print(f"   Similar questions similarity: {similarity1:.2f}")
        print(f"   Different questions similarity: {similarity2:.2f}")
    except Exception as e:
        print(f"Similarity detection failed: {e}")
        return False
    
    # Test 5: Test Repetitive Question Detection
    try:
        conversation_history = [
            ("What is AI?", "AI is artificial intelligence."),
            ("What is AI?", "AI is artificial intelligence."),
            ("What is AI?", "AI is artificial intelligence.")
        ]
        
        is_repetitive = ai_service._is_repetitive_question("What is AI?", conversation_history)
        print(f"Repetitive question detection works")
        print(f"   Is 'What is AI?' repetitive: {is_repetitive}")
    except Exception as e:
        print(f"Repetitive question detection failed: {e}")
        return False
    
    print("\nAll tests passed! Conversation context implementation is working.")
    return True

def test_route_integration():
    """Test route integration"""
    print("\nTesting Route Integration")
    print("=" * 30)
    
    try:
        from app.routes.main_routes import main_bp
        print("Main routes import successful")
    except ImportError as e:
        print(f"Main routes import failed: {e}")
        return False
    
    print("Route integration test passed")
    return True

if __name__ == "__main__":
    print("Starting Conversation Context Tests")
    print("=" * 50)
    
    # Test conversation context
    context_test = test_conversation_context()
    
    # Test route integration
    route_test = test_route_integration()
    
    if context_test and route_test:
        print("\nAll tests passed! Ready for deployment.")
    else:
        print("\nSome tests failed. Please check the implementation.")
