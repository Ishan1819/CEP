from fastapi import FastAPI
from dotenv import load_dotenv
from routes_chatbot import router as chatbot_router

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Include the chatbot router
app.include_router(chatbot_router, prefix="/api/v1", tags=["Chatbot"])

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Chatbot API is running!"}
