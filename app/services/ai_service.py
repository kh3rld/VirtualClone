from transformers import pipeline
import torch
import random
import hashlib
from transformers.utils.logging import set_verbosity_error
from typing import List, Tuple, Optional
set_verbosity_error()

class AIService:
    def __init__(self):
        self.translate_pipe = pipeline("translation", model="facebook/nllb-200-distilled-600M")
        self.qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2",
                                   device=0 if torch.cuda.is_available() else -1)
        self.response_cache = {}
        self.conversation_patterns = {}
    
    def translate(self, text, src_lang, tgt_lang):
        return self.translate_pipe(text, src_lang=src_lang, tgt_lang=tgt_lang)[0]['translation_text']
    
    def answer_question(self, question, context):
        return self.qa_pipeline(question=question, context=context)['answer']
    
    def answer_question_with_context(self, question, base_context, conversation_history=None):
        """
        enhanced answer function that includes conversation history and response diversity
        """
        enhanced_context = self._build_enhanced_context(base_context, conversation_history)
        
        
        question_hash = self._get_question_hash(question)
        if self._is_repetitive_question(question, conversation_history):
            return self._generate_diverse_response(question, enhanced_context, question_hash)
        
        try:
            result = self.qa_pipeline(
                question=question, 
                context=enhanced_context,
                top_k=3,  
                max_answer_len=150
            )
            
            
            response = self._select_diverse_response(result, question, question_hash)
            return response
        except Exception as e:
            print(f"Error in QA pipeline: {e}")
            return "i apologize, but I'm having trouble processing your question right now"
    
    def _build_enhanced_context(self, base_context, conversation_history):
        """
        build enhanced context by combining base context with recent conversation
        """
        if not conversation_history:
            return base_context
        
        
        recent_exchanges = conversation_history[-3:]
        conversation_context = "\n".join([
            f"Previous Question: {q}\nPrevious Answer: {a}\n" 
            for q, a in recent_exchanges
        ])
        
        return f"{base_context}\n\nRecent Conversation Context:\n{conversation_context}"
    
    def _get_question_hash(self, question):
        """
        create a hash for the question to detect similar questions
        """
        
        normalized = question.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _is_repetitive_question(self, question, conversation_history):
        """
        check if the current question is repetitive based on recent conversation
        """
        if not conversation_history:
            return False
        
        
        recent_questions = [q for q, a in conversation_history[-5:]]
        
        
        question_lower = question.lower()
        for recent_q in recent_questions:
            if self._calculate_similarity(question_lower, recent_q.lower()) > 0.7:
                return True
        
        return False
    
    def _calculate_similarity(self, text1, text2):
        """
        implement similarity calculation based on common words
        """
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _generate_diverse_response(self, question, context, question_hash):
        """
        generate a diverse response for repetitive questions
        """
        if question_hash in self.response_cache:
            cached_responses = self.response_cache[question_hash]
            if len(cached_responses) > 1:
                return random.choice([r for r in cached_responses if r != cached_responses[-1]])
        
        try:
            result = self.qa_pipeline(
                question=question, 
                context=context,
                top_k=5,  
                max_answer_len=150
            )
            
            if isinstance(result, list):
                response = random.choice(result[:3])['answer']
            else:
                response = result['answer']
            
            if question_hash not in self.response_cache:
                self.response_cache[question_hash] = []
            self.response_cache[question_hash].append(response)
            
            return response
        except Exception as e:
            print(f"Error generating diverse response: {e}")
            return "i understand you're asking about this topic... lemme provide a different perspective on this..."
    
    def _select_diverse_response(self, result, question, question_hash):
        """
        select the most appropriate response from multiple candidates
        """
        if isinstance(result, list):
            candidates = [r['answer'] for r in result]
            
            unique_candidates = list(dict.fromkeys(candidates))
            
            if len(unique_candidates) > 1:
                response = random.choice(unique_candidates[:2])
            else:
                response = unique_candidates[0]
        else:
            response = result['answer']
        
        if question_hash not in self.response_cache:
            self.response_cache[question_hash] = []
        self.response_cache[question_hash].append(response)
        
        return response

ai_service = AIService()

def translate(text, src_lang, tgt_lang):
    return ai_service.translate(text, src_lang, tgt_lang)

def answer_question(question, context):
    return ai_service.answer_question(question, context)

def answer_question_with_context(question, context, conversation_history=None):
    return ai_service.answer_question_with_context(question, context, conversation_history)
