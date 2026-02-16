from fastapi import FastAPI
from pydantic import BaseModel
from app.rag.retriever import Retriever
from app.services.copilot_service import CopilotService

app = FastAPI(title="Hybrid ANN + RAG Copilot")

class QueryRequest(BaseModel):
    query: str

knowledge_base = [
    "How to apply leave in ERP system",
    "Project assignment workflow",
    "Insurance module details"
]

retriever = Retriever(knowledge_base)
copilot = CopilotService(retriever)

@app.post("/copilot")
def run_copilot(request: QueryRequest):
    intent = "sample_intent"  # Replace with ANN inference
    response = copilot.generate_response(intent, request.query)
    return response
