from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class User(SQLModel, table=True):
    __tablename__ = "users"  # Nom exact de la table
    id: str = Field(default=None, primary_key=True)
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    username: str = Field(max_length=50, unique=True)
    email: str = Field(max_length=100, unique=True)
    password_hash: str = Field(max_length=255)
    admin: bool = Field(default=False)
    created_at: Optional[datetime] = Field(default=None)
    bio: Optional[str] = None
    description: Optional[str] = None
    otp: Optional[int] = None
    session_cookie: Optional[str] = None
    profile_image: Optional[str] = None
    window_location: Optional[str] = None

class Report(SQLModel, table=True):
    __tablename__ = "reports"  # Nom exact de la table
    id: Optional[int] = Field(default=None, primary_key=True)
    reported_user_id: str = Field(foreign_key="users.id")
    reporter_user_id: str = Field(foreign_key="users.id")
    reason: Optional[str] = None
    report_date: Optional[datetime] = Field(default=None)

class FriendRequest(SQLModel, table=True):
    __tablename__ = "friend_requests"  # Nom exact de la table
    request_id: Optional[int] = Field(default=None, primary_key=True)
    requester_id: UUID = Field(foreign_key="users.id")
    receiver_id: UUID = Field(foreign_key="users.id")
    requester_first_name: str
    requester_last_name: str
    request_date: Optional[datetime] = Field(default=None)

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"  # Nom exact de la table
    id: str = Field(primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    contact_id: str = Field(foreign_key="users.id")
    last_message: Optional[str] = None
    publish_at: Optional[datetime] = Field(default=None)

class Contact(SQLModel, table=True):
    __tablename__ = "contacts"  # Nom exact de la table
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    contact_id: str = Field(foreign_key="users.id")
    last_message: Optional[str] = None
    last_message_date: Optional[datetime] = None
    unread_messages_count: Optional[int] = Field(default=0)