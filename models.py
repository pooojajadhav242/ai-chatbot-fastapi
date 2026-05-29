from sqlalchemy import Column, Integer, String
from database import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column( Integer, primary_key = True, index = True)
    username = Column(String)
    role = Column(String)
    message = Column(String)