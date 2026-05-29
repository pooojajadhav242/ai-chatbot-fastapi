from fastapi import FastAPI
from google import genai
from pydantic import BaseModel
from fastapi import HTTPException
import json
import os
from dotenv import load_dotenv
from datetime import datetime
from fastapi import Depends
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from database import engine,Base
from database import get_db
from models import ChatMessage
from sqlalchemy.orm import Session
from auth import create_access_token
from auth import verify_token
from fastapi import Header
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials



app = FastAPI()

Base.metadata.create_all(bind=engine)

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(
    api_key= api_key
)

def get_current_time():
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

@app.get("/")
def home():
    return {
        "message": "AI API Working"
    }

class AIRequest(BaseModel):
    username:str
    question:str

class LoginRequest(BaseModel):
    username:str
    password:str


@app.post("/login")
def login(request:LoginRequest):
    if(request.username == "Pooja" and request.password == "1234"):
        token = create_access_token({"sub":request.username})
        return {"access_token" : token}
    return {"message" : "Invalid credentials"}  

from fastapi import Header
from auth import verify_token

security = HTTPBearer()

@app.get("/protected")
def protected_route(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    payload = verify_token(token)

    if not payload:
        return {"message": "Invalid token"}

    return {
        "message": "Access granted",
        "user": payload
    }
   
    
def save_chat_sessions():
    
    with open("new_chat_history.json","w") as file:
        json.dump(chat_sessions,file,indent=4)

        

def load_chat_sessions():
    global chat_sessions

    if os.path.exists("new_chat_history.json"):
        with open("new_chat_history.json","r") as file:
            chat_sessions = json.load(file) 

chat_sessions = {}
load_chat_sessions()

@app.post("/ask-ai")
def ask_ai(request:AIRequest, db: Session = Depends(get_db)):
    username = request.username

    if(username not in chat_sessions):
        chat_sessions[username] = []

    db.add(ChatMessage(
        username = username,
        role="User",
        message=request.question
    ))
    db.commit()
  
    prompt = ""

    for chat in chat_sessions[username]:
        prompt += (
            f"{chat['role']}: "
            f"{chat['message']}\n"
            )

    try:
        response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
        )

    except Exception as e:
        error_message = str(e)

        if "429" in error_message:

            raise HTTPException(

                status_code=429,

                detail=
                "Too many requests 😄 Please wait a little and try again."
            )

        raise HTTPException(

            status_code=500,

            detail=
            "Something went wrong with AI response."
        ) 

    chat_sessions[username].append({
        "role": "AI",
        "message": response.text,
        "time":get_current_time()
    })

    db.add(ChatMessage(
        username = username,
        role="AI",
        message=response.text
    ))
    db.commit()
    
    return {
        "username":username,
        "answer" : response.text
    }

@app.get("/reset-api")
def reset_api(username:str):
    if username in chat_sessions:
        del chat_sessions[username]
        save_chat_sessions()
        return {"message": f"{username} chat deleted"}

    return {"message":"User not found"}


@app.get("/health")
def health_check():
    try:
        response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents="Hello Gemini"
        )
        return {
            "status":"healthy",
            "ai_model":"working"
        }
    except Exception as e:
        return {
            "status" : "unhealthy",
            "error" :str(e)
        }

@app.get("/all_chats")
def get_all_chats(db: Session = Depends(get_db)):
    chats = db.query(ChatMessage).all()
    return chats       


@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):

    test_chat = ChatMessage(
        username="test",
        role="User",
        message="Hello DB"
    )

    db.add(test_chat)
    db.commit()

    return {"message": "Inserted"}    


@app.get("/chat_history/{username}")
def get_chat_hitory(username:str, db: Session = Depends(get_db)):
    chats = db.query(ChatMessage).filter(
        ChatMessage.username == username
    ).all()
    return chats    

@app.get("/delete_chat_history/{id}")
def delete_chat_history(id:int, db:Session = Depends(get_db)):
    chat = db.query(ChatMessage).filter(ChatMessage.id == id).first()

    if(not chat):
        return {"message":"Chat not found"}
    db.delete(chat)
    db.commit()

    return {"message":"Chat deleted successfully"}

class UpdateMessage(BaseModel):
    message:str

@app.put("/update-chat/{chat_id}")
def update_chat(chat_id:int, request:UpdateMessage, db: Session = Depends(get_db)):
    chat = db.query(ChatMessage).filter(ChatMessage.id == chat_id).first()

    if not chat:
        return {"message" : "Chat not found"}

    chat.message = request.message
    db.commit()

    return {"message": "Chat updated successfully"}    
