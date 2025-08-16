from fastapi import APIRouter, HTTPException, Body
from app.services import watsonx_client

router = APIRouter()

@router.post("/chat")
async def chat_with_watsonx(
    message: str = Body(..., embed=True, description="User's message to Watsonx assistant")
):
    """
    Send user message to Watsonx.ai and return structured assistant reply.
    """
    try:
        reply = watsonx_client.ask_watsonx(message)
        if reply.get("intent") == "error":
            raise HTTPException(status_code=502, detail=reply["response"])
        return {"status": "ok", "assistant_reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Watsonx.ai error: {str(e)}")
