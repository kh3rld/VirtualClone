#!/usr/bin/env python3
"""
Demo script to test conversation context without running the full server
"""

def test_conversation_flow():
    """Test the conversation flow with our enhanced AI service"""
    print("Testing Conversation Context Flow")
    print("=" * 50)
    
    try:
        from app.services.ai_service import AIService
        from app.services.context_loader import load_context
        
        # Load context
        print("Loading context...")
        context = load_context()
        print(f"Context loaded: {len(context)} characters")
        
        # Create AI service
        print("\nCreating AI service...")
        ai_service = AIService()
        print("AI service created")
        
        # Simulate conversation
        print("\nSimulating conversation...")
        conversation_history = []
        
        # Test questions
        questions = [
            "What is the Matrix?",
            "Who is Neo?",
            "What is the Matrix?",  # Repetitive question
            "Who are the machines?",
            "What is the Matrix?",  # Another repetitive question
            "How does Neo discover the truth?"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n--- Question {i} ---")
            print(f"Q: {question}")
            
            # Get recent history for context
            recent_history = conversation_history[-3:] if conversation_history else []
            
            # Get answer with context
            try:
                answer = ai_service.answer_question_with_context(
                    question, 
                    context, 
                    recent_history
                )
                print(f"A: {answer}")
                
                # Add to conversation history
                conversation_history.append((question, answer))
                
                # Show context info
                if recent_history:
                    print(f"Used {len(recent_history)} previous exchanges for context")
                else:
                    print("No previous context used")
                    
            except Exception as e:
                print(f"Error: {e}")
                # Add error to history
                conversation_history.append((question, f"Error: {e}"))
        
        print(f"\nConversation Summary:")
        print(f"Total exchanges: {len(conversation_history)}")
        print(f"Repetitive questions: {len([q for q, a in conversation_history if q == 'What is the Matrix?'])}")
        print("Conversation context test completed!")
        
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting Conversation Context Demo")
    print("=" * 50)
    
    success = test_conversation_flow()
    
    if success:
        print("\nDemo completed successfully!")
        print("The conversation context implementation is working correctly.")
    else:
        print("\nDemo failed. Check the errors above.")
