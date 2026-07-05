from fastapi import APIRouter, Depends, HTTPException
from app.ai.agents.analysis_agent import AnalysisAgent
from app.ai.agents.recommendation_agent import RecommendationAgent
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/agents", tags=["AI Agents"])

@router.get("/alerts")
async def get_alerts(user: dict = Depends(get_current_user)):
    agent = AnalysisAgent()
    analysis = await agent.analyze()
    return analysis

@router.get("/recommendations")
async def get_recommendations(user: dict = Depends(get_current_user)):
    agent = RecommendationAgent()
    recommendations = await agent.get_recommendations()
    return recommendations
