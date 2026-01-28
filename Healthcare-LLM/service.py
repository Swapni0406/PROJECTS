import os
import json
from typing import List, Optional
from openai import OpenAI
from app.models import (
    AnalysisResponse, ChatResponse, ChatMessage, 
    HealthMetric, HealthInsight, ReportComparison
)
from app.utils.prompts import (
    ANALYSIS_PROMPT, CHAT_PROMPT, TERM_EXPLANATION_PROMPT,
    COMPARISON_PROMPT
)


class LLMService:
    """Service for interacting with LLM for medical analysis"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def analyze_medical_report(self, report_text: str) -> AnalysisResponse:
        """
        Analyze a medical report using LLM
        
        Args:
            report_text: Extracted text from medical report
        
        Returns:
            Structured analysis response
        """
        prompt = ANALYSIS_PROMPT.format(report_text=report_text)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical AI assistant that helps patients understand their medical reports. Provide accurate, compassionate, and easy-to-understand explanations."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Lower temperature for more consistent medical advice
            response_format={"type": "json_object"}
        )
        
        # Parse LLM response
        analysis_data = json.loads(response.choices[0].message.content)
        
        # Convert to Pydantic models
        return AnalysisResponse(
            report_type=analysis_data.get("report_type", "Unknown"),
            original_text=report_text,
            patient_friendly_summary=analysis_data.get("patient_friendly_summary", ""),
            key_findings=[
                HealthMetric(**finding) 
                for finding in analysis_data.get("key_findings", [])
            ],
            health_insights=[
                HealthInsight(**insight)
                for insight in analysis_data.get("health_insights", [])
            ],
            risk_factors=analysis_data.get("risk_factors", []),
            positive_indicators=analysis_data.get("positive_indicators", []),
            medical_terminology_explained=analysis_data.get("medical_terminology_explained", {})
        )
    
    def chat(
        self, 
        message: str, 
        context: Optional[str] = None,
        conversation_history: Optional[List[ChatMessage]] = None
    ) -> ChatResponse:
        """
        Chat with the health assistant
        
        Args:
            message: User's question
            context: Optional context (e.g., previous report)
            conversation_history: Previous conversation messages
        
        Returns:
            AI response with suggestions
        """
        # Build conversation messages
        messages = [
            {
                "role": "system",
                "content": CHAT_PROMPT
            }
        ]
        
        # Add context if provided
        if context:
            messages.append({
                "role": "system",
                "content": f"Previous report context:\n{context}"
            })
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-6:]:  # Last 6 messages for context
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content
        
        # Generate follow-up questions
        suggested_questions = self._generate_follow_up_questions(message, response_text)
        
        return ChatResponse(
            response=response_text,
            suggested_questions=suggested_questions
        )
    
    def explain_medical_term(self, term: str) -> str:
        """
        Explain a medical term in simple language
        
        Args:
            term: Medical terminology
        
        Returns:
            Simple explanation
        """
        prompt = TERM_EXPLANATION_PROMPT.format(term=term)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical educator helping patients understand medical terminology."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )
        
        return response.choices[0].message.content
    
    def compare_reports(self, report1_text: str, report2_text: str) -> ReportComparison:
        """
        Compare two medical reports to identify trends
        
        Args:
            report1_text: First report (older)
            report2_text: Second report (newer)
        
        Returns:
            Comparison analysis
        """
        prompt = COMPARISON_PROMPT.format(
            report1=report1_text,
            report2=report2_text
        )
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical AI analyzing trends in patient health reports."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        comparison_data = json.loads(response.choices[0].message.content)
        
        return ReportComparison(**comparison_data)
    
    def _generate_follow_up_questions(self, user_message: str, ai_response: str) -> List[str]:
        """Generate relevant follow-up questions"""
        # Simple implementation - can be enhanced with another LLM call
        questions = [
            "What lifestyle changes can I make to improve these results?",
            "Should I be concerned about any of these findings?",
            "How often should I get these tests done?"
        ]
        return questions[:3]
