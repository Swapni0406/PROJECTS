from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv

from app.services.llm_service import LLMService
from app.services.report_parser import ReportParser
from app.models import AnalysisResponse, ChatRequest, ChatResponse, HealthInsight

load_dotenv()

app = FastAPI(
    title="Healthcare LLM Assistant API",
    description="AI-powered medical report analyzer and health assistant",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
llm_service = LLMService(api_key=os.getenv("OPENAI_API_KEY"))
report_parser = ReportParser()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Healthcare LLM Assistant API is running",
        "version": "1.0.0"
    }


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_report(file: UploadFile = File(...)):
    """
    Analyze a medical report and provide patient-friendly insights
    
    Args:
        file: Medical report (PDF, TXT, or image)
    
    Returns:
        Analysis with simplified explanation and health insights
    """
    try:
        # Validate file type
        allowed_types = ["application/pdf", "text/plain", "image/png", "image/jpeg"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: PDF, TXT, PNG, JPEG"
            )
        
        # Read and parse the report
        content = await file.read()
        extracted_text = report_parser.extract_text(content, file.content_type)
        
        if not extracted_text or len(extracted_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Could not extract meaningful text from the report"
            )
        
        # Analyze with LLM
        analysis = llm_service.analyze_medical_report(extracted_text)
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the health assistant about medical reports
    
    Args:
        request: Chat message and optional context
    
    Returns:
        AI-generated response
    """
    try:
        response = llm_service.chat(
            message=request.message,
            context=request.context,
            conversation_history=request.conversation_history
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/explain-term")
async def explain_medical_term(term: str):
    """
    Explain a medical term in simple language
    
    Args:
        term: Medical terminology to explain
    
    Returns:
        Simple explanation
    """
    try:
        explanation = llm_service.explain_medical_term(term)
        return {"term": term, "explanation": explanation}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/compare-reports")
async def compare_reports(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...)
):
    """
    Compare two medical reports to identify trends
    
    Args:
        file1: First medical report
        file2: Second medical report
    
    Returns:
        Comparison analysis highlighting changes
    """
    try:
        # Parse both reports
        content1 = await file1.read()
        content2 = await file2.read()
        
        text1 = report_parser.extract_text(content1, file1.content_type)
        text2 = report_parser.extract_text(content2, file2.content_type)
        
        # Compare using LLM
        comparison = llm_service.compare_reports(text1, text2)
        
        return comparison
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
