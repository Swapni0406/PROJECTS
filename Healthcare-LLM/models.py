from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class HealthMetric(BaseModel):
    """Individual health metric from a report"""
    name: str
    value: str
    unit: Optional[str] = None
    normal_range: Optional[str] = None
    status: str  # "normal", "high", "low", "critical"
    interpretation: str


class HealthInsight(BaseModel):
    """Health insight or recommendation"""
    category: str  # "diet", "exercise", "medication", "lifestyle"
    priority: str  # "high", "medium", "low"
    recommendation: str
    reasoning: str


class AnalysisResponse(BaseModel):
    """Response from report analysis"""
    report_type: str
    original_text: str
    patient_friendly_summary: str
    key_findings: List[HealthMetric]
    health_insights: List[HealthInsight]
    risk_factors: List[str]
    positive_indicators: List[str]
    medical_terminology_explained: Dict[str, str]
    timestamp: datetime = Field(default_factory=datetime.now)
    disclaimer: str = (
        "This analysis is for informational purposes only and should not "
        "replace professional medical advice. Please consult with your "
        "healthcare provider for medical decisions."
    )


class ChatMessage(BaseModel):
    """Individual chat message"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """Request for chat endpoint"""
    message: str
    context: Optional[str] = None  # Previous report or context
    conversation_history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    """Response from chat endpoint"""
    response: str
    suggested_questions: Optional[List[str]] = None
    references: Optional[List[str]] = None


class ReportComparison(BaseModel):
    """Comparison between two reports"""
    improvements: List[str]
    deteriorations: List[str]
    stable_metrics: List[str]
    trend_analysis: str
    recommendations: List[str]
