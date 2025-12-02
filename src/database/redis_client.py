"""
Redis client for Niniko
Handles all Redis database operations
"""

import json
import logging
from typing import Optional, Dict, Any, List
from upstash_redis.asyncio import Redis

from src.config import config
from src.database.models import UserProfile, CallRecord

logger = logging.getLogger(__name__)


class RedisClient:
    """Async Redis client for Niniko"""
    
    def __init__(self):
        """Initialize Redis client"""
        self.redis: Optional[Redis] = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize the Redis connection"""
        if self._initialized:
            return
        
        try:
            self.redis = Redis(
                url=config.UPSTASH_REDIS_REST_URL,
                token=config.UPSTASH_REDIS_REST_TOKEN
            )
            
            # Test connection
            await self.redis.ping()
            self._initialized = True
            logger.info("✓ Redis client initialized successfully")
            
        except Exception as e:
            logger.error(f"✗ Failed to initialize Redis client: {e}")
            raise
    
    def ensure_initialized(self):
        """Ensure Redis client is initialized"""
        if not self._initialized:
            raise RuntimeError("Redis client not initialized. Call initialize() first.")
    
    # ==================== User Profile Operations ====================
    
    async def get_user_by_phone(self, phone_number: str) -> Optional[UserProfile]:
        """
        Get user profile by phone number
        
        Args:
            phone_number: User's phone number (e.g., "+30xxxxxxxxxx")
        
        Returns:
            UserProfile if found, None otherwise
        """
        self.ensure_initialized()
        
        try:
            # Look up user_id by phone number
            user_id = await self.redis.get(f"niniko:phone:{phone_number}")
            
            if not user_id:
                logger.debug(f"No user found with phone number: {phone_number}")
                return None
            
            # Get user profile
            return await self.get_user_profile(user_id)
            
        except Exception as e:
            logger.error(f"Error getting user by phone {phone_number}: {e}")
            return None
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Get user profile by user_id
        
        Args:
            user_id: User's unique identifier
        
        Returns:
            UserProfile if found, None otherwise
        """
        self.ensure_initialized()
        
        try:
            data = await self.redis.hgetall(f"niniko:user:{user_id}")
            
            if not data:
                logger.debug(f"No user profile found for user_id: {user_id}")
                return None
            
            # Deserialize JSON fields
            if 'interests' in data:
                data['interests'] = json.loads(data['interests'])
            if 'favorite_topics' in data:
                data['favorite_topics'] = json.loads(data['favorite_topics'])
            if 'avoid_topics' in data:
                data['avoid_topics'] = json.loads(data['avoid_topics'])
            
            return UserProfile.from_redis_dict(data)
            
        except Exception as e:
            logger.error(f"Error getting user profile {user_id}: {e}")
            return None
    
    async def create_user(self, user_profile: UserProfile) -> bool:
        """
        Create a new user profile
        
        Args:
            user_profile: UserProfile object to create
        
        Returns:
            True if successful, False otherwise
        """
        self.ensure_initialized()
        
        try:
            # Check if phone number already exists
            existing_user_id = await self.redis.get(f"niniko:phone:{user_profile.phone_number}")
            if existing_user_id:
                logger.warning(f"User with phone {user_profile.phone_number} already exists")
                return False
            
            # Convert to Redis-compatible format
            data = user_profile.to_redis_dict()
            
            # Serialize list fields to JSON
            data['interests'] = json.dumps(data['interests'])
            data['favorite_topics'] = json.dumps(data['favorite_topics'])
            data['avoid_topics'] = json.dumps(data['avoid_topics'])
            
            # Store user profile as hash
            await self.redis.hset(f"niniko:user:{user_profile.user_id}", data)
            
            # Create phone number index
            await self.redis.set(
                f"niniko:phone:{user_profile.phone_number}",
                user_profile.user_id
            )
            
            # Add to users set
            await self.redis.sadd("niniko:users", user_profile.user_id)
            
            logger.info(f"✓ Created user profile for {user_profile.name} ({user_profile.phone_number})")
            return True
            
        except Exception as e:
            logger.error(f"Error creating user profile: {e}")
            return False
    
    async def update_user(self, user_profile: UserProfile) -> bool:
        """
        Update existing user profile
        
        Args:
            user_profile: UserProfile object with updated data
        
        Returns:
            True if successful, False otherwise
        """
        self.ensure_initialized()
        
        try:
            # Convert to Redis-compatible format
            data = user_profile.to_redis_dict()
            
            # Serialize list fields to JSON
            data['interests'] = json.dumps(data['interests'])
            data['favorite_topics'] = json.dumps(data['favorite_topics'])
            data['avoid_topics'] = json.dumps(data['avoid_topics'])
            
            # Update user profile
            await self.redis.hset(f"niniko:user:{user_profile.user_id}", data)
            
            logger.info(f"✓ Updated user profile for {user_profile.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return False
    
    # ==================== Call History Operations ====================
    
    async def save_call_record(self, call_record: CallRecord) -> bool:
        """
        Save a call history record
        
        Args:
            call_record: CallRecord object to save
        
        Returns:
            True if successful, False otherwise
        """
        self.ensure_initialized()
        
        try:
            # Convert to Redis-compatible format
            data = call_record.to_redis_dict()
            data['topics'] = json.dumps(data['topics'])
            
            # Store call record as hash
            await self.redis.hset(
                f"niniko:call:{call_record.user_id}:{call_record.call_id}",
                data
            )
            
            # Add to user's call history list (sorted by timestamp)
            await self.redis.zadd(
                f"niniko:user:{call_record.user_id}:calls",
                {call_record.call_id: call_record.timestamp.timestamp()}
            )
            
            logger.info(f"✓ Saved call record {call_record.call_id} for user {call_record.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving call record: {e}")
            return False
    
    async def get_recent_calls(self, user_id: str, limit: int = 10) -> List[CallRecord]:
        """
        Get recent call records for a user
        
        Args:
            user_id: User's unique identifier
            limit: Maximum number of records to return
        
        Returns:
            List of CallRecord objects (most recent first)
        """
        self.ensure_initialized()
        
        try:
            # Get call IDs sorted by timestamp (descending)
            call_ids = await self.redis.zrevrange(
                f"niniko:user:{user_id}:calls",
                0,
                limit - 1
            )
            
            if not call_ids:
                return []
            
            # Fetch call records
            calls = []
            for call_id in call_ids:
                data = await self.redis.hgetall(f"niniko:call:{user_id}:{call_id}")
                if data:
                    # Deserialize JSON fields
                    if 'topics' in data:
                        data['topics'] = json.loads(data['topics'])
                    calls.append(CallRecord.from_redis_dict(data))
            
            return calls
            
        except Exception as e:
            logger.error(f"Error getting recent calls for user {user_id}: {e}")
            return []
    
    # ==================== Stats and Utility Operations ====================
    
    async def get_total_users(self) -> int:
        """Get total number of registered users"""
        self.ensure_initialized()
        
        try:
            count = await self.redis.scard("niniko:users")
            return count or 0
        except Exception as e:
            logger.error(f"Error getting total users: {e}")
            return 0
    
    async def get_all_user_ids(self) -> List[str]:
        """Get all user IDs"""
        self.ensure_initialized()
        
        try:
            user_ids = await self.redis.smembers("niniko:users")
            return list(user_ids) if user_ids else []
        except Exception as e:
            logger.error(f"Error getting all user IDs: {e}")
            return []
    
    async def close(self):
        """Close Redis connection"""
        # Upstash Redis client doesn't need explicit closing
        # but we mark as uninitialized
        self._initialized = False
        logger.info("Redis client closed")


# Global Redis client instance
redis_client = RedisClient()
