"""
Pydantic data models for Niniko system
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import uuid4


def generate_uuid() -> str:
    """Generate a UUID string"""
    return str(uuid4())


class UserProfile(BaseModel):
    """User profile data model"""
    user_id: str = Field(default_factory=generate_uuid)
    phone_number: str
    name: str
    preferred_name: Optional[str] = None
    registration_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = "active"  # active, inactive, suspended
    timezone: str = "Europe/Athens"
    
    # Preferences
    interests: List[str] = Field(default_factory=list)
    favorite_topics: List[str] = Field(default_factory=list)
    avoid_topics: List[str] = Field(default_factory=list)
    preferred_greeting: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_redis_dict(self) -> Dict[str, Any]:
        """Convert to dictionary suitable for Redis storage"""
        data = self.model_dump()
        # Convert datetime to ISO string
        data['registration_date'] = self.registration_date.isoformat()
        return data
    
    @classmethod
    def from_redis_dict(cls, data: Dict[str, Any]) -> "UserProfile":
        """Create UserProfile from Redis dictionary"""
        if 'registration_date' in data and isinstance(data['registration_date'], str):
            data['registration_date'] = datetime.fromisoformat(data['registration_date'])
        return cls(**data)


class CallRecord(BaseModel):
    """Call history record"""
    call_id: str = Field(default_factory=generate_uuid)
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration_seconds: int = 0
    summary: Optional[str] = None
    mood: Optional[str] = None  # positive, neutral, negative, concerned
    topics: List[str] = Field(default_factory=list)
    emergency_detected: bool = False
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_redis_dict(self) -> Dict[str, Any]:
        """Convert to dictionary suitable for Redis storage"""
        data = self.model_dump()
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_redis_dict(cls, data: Dict[str, Any]) -> "CallRecord":
        """Create CallRecord from Redis dictionary"""
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class UserPreferences(BaseModel):
    """User preferences and conversation context"""
    user_id: str
    interests: List[str] = Field(default_factory=list)
    favorite_topics: List[str] = Field(default_factory=list)
    avoid_topics: List[str] = Field(default_factory=list)
    preferred_greeting: str = "Καλημέρα"
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
