from fastapi import APIRouter, HTTPException
from supabase_client import insert_data
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
import os
import requests

# Load environment variables
GEMINI_KEY = os.getenv("GEMINI_KEY")

# FastAPI Router
router = APIRouter()

# Pydantic Models
class SignupRequest(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    password: str
    city: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SubmitDataRequest(BaseModel):
    user_id: str
    data_type: str = Field(..., example="feedback")
    content: str

class ChatbotRequest(BaseModel):
    user_id: str
    query: str


# Gemini API logic
def get_gemini_response(query: str, system_prompt: str = "") -> str:
    url = "e.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=GAIzaSyCN-73I9hVAD6Idzq5pP0L3mboOxbIZTv4"  # Replace with actual Gemini API endpoint
    headers = {"Authorization": f"Bearer {GEMINI_KEY}"}
    
    payload = {
        "query": query,
        "system_prompt": system_prompt,  # Include system prompt if required
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch response from Gemini API")

    return response.json().get("response", "No response available")


query = "How do I install Python on Windows?"
response = get_gemini_response(query, system_prompt="You are an expert in programming and development, assisting with Python installation.")
print(response)


# Endpoints
@router.post("/signup")
async def signup(request: SignupRequest):
    data = {
        "user_id": request.user_id,
        "name": request.name,
        "email": request.email,
        "password": request.password,  # Use hashed passwords in production
        "city": request.city,
        "created_at": datetime.utcnow().isoformat()
    }

    try:
        insert_data("users", data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")
    
    return {"message": "Signup successful"}

@router.post("/login")
async def login(request: LoginRequest):
    try:
        user = fetch_data("users", {"email": request.email, "password": request.password})
        if not user.data:
            raise HTTPException(status_code=401, detail="Invalid email or password")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

    return {"message": "Login successful", "user_id": user.data[0]["user_id"]}

@router.post("/submit")
async def submit_data(request: SubmitDataRequest):
    data = {
        "user_id": request.user_id,
        "data_type": request.data_type,
        "content": request.content,
        "created_at": datetime.utcnow().isoformat()
    }

    try:
        insert_data("user_submissions", data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data submission failed: {str(e)}")

    return {"message": "Data submitted successfully"}

@router.post("/chat")
async def get_response(request: ChatbotRequest):
    try:
        # Fetch response from Gemini API
        response = get_gemini_response(request.query)

        # Save query and response to Supabase
        data = {
            "user_id": request.user_id,
            "query": request.query,
            "response": response,
            "created_at": datetime.utcnow().isoformat()
        }
        insert_data("chatbot_data", data)

        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")
