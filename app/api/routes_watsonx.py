from fastapi import APIRouter

router = APIRouter()

@router.post("/chat")
async def watsonx_chat(query: str):
    return {"query": query, "response": "Watsonx mock response"}
