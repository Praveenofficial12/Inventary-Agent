from fastapi import APIRouter, Depends, Body
from app.ai.agents.assistant_agent import AssistantAgent
from app.auth.dependencies import get_current_user
from app.db.mongo import get_database
from datetime import datetime

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/message")
async def send_message(
    session_id: str = Body(..., embed=True),
    message: str = Body(..., embed=True),
    user: dict = Depends(get_current_user)
):
    agent = AssistantAgent(session_id)
    response = await agent.get_response(message)
    
    # Store in history
    db = get_database()
    await db.chats.update_one(
        {"session_id": session_id, "user_id": user["email"]},
        {
            "$push": {
                "messages": [
                    {"role": "user", "content": message, "created_at": datetime.utcnow()},
                    {"role": "assistant", "content": response, "created_at": datetime.utcnow()}
                ]
            },
            "$setOnInsert": {"created_at": datetime.utcnow()}
        },
        upsert=True
    )
    
    return {"content": response}

@router.get("/history/{session_id}")
async def get_history(session_id: str, user: dict = Depends(get_current_user)):
    db = get_database()
    chat = await db.chats.find_one({"session_id": session_id, "user_id": user["email"]})
    if not chat:
        return {"messages": []}
    return {"messages": chat["messages"]}
