from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from chatbot import HotelChatbot
import uvicorn

app = FastAPI(title="Hotel Recommendation Chatbot API")
chatbot = HotelChatbot()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    status: str
    response: str | None = None
    error: str | None = None

@app.post("/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    """
    Endpoint to handle hotel recommendation queries
    """
    try:
        result = chatbot.process_query(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 