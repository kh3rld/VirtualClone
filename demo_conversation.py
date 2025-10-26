#!/usr/bin/env python3
"""
Demo script showing conversation context functionality
"""

def demo_conversation_context():
    """Demonstrate conversation context features"""
    print("Conversation Context Demo")
    print("=" * 40)
    
    base_context = """
    The Matrix is a 1999 science fiction action film written and directed by the Wachowskis. 
    It stars Keanu Reeves as Neo, a computer programmer who discovers that reality is a simulation 
    called the Matrix, created by intelligent machines to subdue humanity.
    """
    
    conversation_history = []
    
    questions = [
        "What is the Matrix?",
        "Who is Neo?",
        "What is the Matrix?", 
        "Who are the machines?",
        "What is the Matrix?",  
        "How does Neo discover the truth?"
    ]
    
    print("Simulating conversation with context awareness...")
    print()
    
    for i, question in enumerate(questions, 1):
        print(f"Question {i}: {question}")
        
        
        if conversation_history:
            recent_context = "\n".join([
                f"Previous Q: {q}\nPrevious A: {a}\n" 
                for q, a in conversation_history[-2:]
            ])
            enhanced_context = f"{base_context}\n\nRecent Context:\n{recent_context}"
        else:
            enhanced_context = base_context
        
        
        if "Matrix" in question and len([q for q, a in conversation_history if "Matrix" in q]) > 0:
            answer = f"Based on our previous discussion, the Matrix is a simulation. (Context-aware response #{i})"
        else:
            answer = f"This is a response about the Matrix. (Response #{i})"
        
        conversation_history.append((question, answer))
        print(f"Answer {i}: {answer}")
        print(f"Context length: {len(enhanced_context)} characters")
        print("-" * 40)
    
    print("\nConversation Summary:")
    print(f"Total exchanges: {len(conversation_history)}")
    print(f"Repetitive questions detected: {len([q for q, a in conversation_history if q == 'What is the Matrix?'])}")
    print("Context awareness demonstrated!")

if __name__ == "__main__":
    demo_conversation_context()
