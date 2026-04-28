from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import os
import uvicorn
from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.outreach_agent import OutreachAgent
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Elite AI Lead Intelligence API")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    company_name: str
    company_url: str

@app.get("/")
def read_root():
    return {"status": "Elite AI Backend is Online"}

@app.post("/analyze")
async def run_analysis(request: AnalysisRequest):
    try:
        # 1. Research phase
        research_agent = ResearchAgent()
        research_data = research_agent.execute(request.company_name, request.company_url)
        
        # 2. Analysis phase
        analysis_agent = AnalysisAgent()
        analysis_data = analysis_agent.analyze(research_data)
        
        # 3. Outreach phase
        outreach_agent = OutreachAgent()
        outreach_data = outreach_agent.generate(analysis_data)
        
        return {
            "company_name": request.company_name,
            "research": research_data,
            "analysis": analysis_data,
            "outreach": outreach_data,
            "timestamp": "Real-time"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
