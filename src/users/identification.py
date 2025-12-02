"""
User identification service
Handles user identification by phone number and registration flow
"""

import logging
from typing import Optional, Tuple
from datetime import datetime

from src.database.redis_client import redis_client
from src.database.models import UserProfile
from src.utils.phone_numbers import normalize_phone_number, format_phone_display

logger = logging.getLogger(__name__)


class UserIdentificationService:
    """Service for identifying and managing users"""
    
    def __init__(self):
        self.redis = redis_client
    
    async def identify_user(self, phone_number: str) -> Tuple[Optional[UserProfile], bool]:
        """
        Identify user by phone number
        
        Args:
            phone_number: User's phone number (any format)
        
        Returns:
            Tuple of (UserProfile or None, is_new_user)
            - If user found: (UserProfile, False)
            - If user not found: (None, True)
            - If error: (None, False)
        """
        # Normalize phone number
        normalized_phone = normalize_phone_number(phone_number)
        if not normalized_phone:
            logger.warning(f"Invalid phone number format: {phone_number}")
            return None, False
        
        logger.info(f"Identifying user with phone: {format_phone_display(normalized_phone)}")
        
        # Look up user in database
        user_profile = await self.redis.get_user_by_phone(normalized_phone)
        
        if user_profile:
            logger.info(f"✓ User identified: {user_profile.name} (ID: {user_profile.user_id})")
            return user_profile, False
        else:
            logger.info(f"✗ User not found with phone: {format_phone_display(normalized_phone)}")
            return None, True
    
    async def register_new_user(
        self,
        phone_number: str,
        name: str,
        preferred_name: Optional[str] = None
    ) -> Optional[UserProfile]:
        """
        Register a new user
        
        Args:
            phone_number: User's phone number (any format)
            name: User's full name
            preferred_name: How the user prefers to be addressed
        
        Returns:
            UserProfile if successful, None otherwise
        """
        # Normalize phone number
        normalized_phone = normalize_phone_number(phone_number)
        if not normalized_phone:
            logger.error(f"Cannot register user with invalid phone: {phone_number}")
            return None
        
        # Create user profile
        user_profile = UserProfile(
            phone_number=normalized_phone,
            name=name,
            preferred_name=preferred_name or name.split()[0],  # Use first name as default
            registration_date=datetime.utcnow(),
            status="active",
            timezone="Europe/Athens"
        )
        
        # Save to database
        success = await self.redis.create_user(user_profile)
        
        if success:
            logger.info(f"✓ Registered new user: {name} ({format_phone_display(normalized_phone)})")
            return user_profile
        else:
            logger.error(f"✗ Failed to register user: {name}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserProfile]:
        """
        Get user profile by user_id
        
        Args:
            user_id: User's unique identifier
        
        Returns:
            UserProfile if found, None otherwise
        """
        return await self.redis.get_user_profile(user_id)
    
    async def update_user_preferences(
        self,
        user_id: str,
        interests: Optional[list] = None,
        favorite_topics: Optional[list] = None,
        avoid_topics: Optional[list] = None,
        preferred_greeting: Optional[str] = None
    ) -> bool:
        """
        Update user preferences
        
        Args:
            user_id: User's unique identifier
            interests: List of user interests
            favorite_topics: List of favorite conversation topics
            avoid_topics: List of topics to avoid
            preferred_greeting: Preferred greeting phrase
        
        Returns:
            True if successful, False otherwise
        """
        # Get current profile
        user_profile = await self.redis.get_user_profile(user_id)
        if not user_profile:
            logger.error(f"Cannot update preferences - user not found: {user_id}")
            return False
        
        # Update fields if provided
        if interests is not None:
            user_profile.interests = interests
        if favorite_topics is not None:
            user_profile.favorite_topics = favorite_topics
        if avoid_topics is not None:
            user_profile.avoid_topics = avoid_topics
        if preferred_greeting is not None:
            user_profile.preferred_greeting = preferred_greeting
        
        # Save updated profile
        success = await self.redis.update_user(user_profile)
        
        if success:
            logger.info(f"✓ Updated preferences for user: {user_id}")
        else:
            logger.error(f"✗ Failed to update preferences for user: {user_id}")
        
        return success
    
    async def generate_user_context(self, user_profile: UserProfile) -> str:
        """
        Generate context string for LLM about the user
        
        Args:
            user_profile: User's profile
        
        Returns:
            Context string to inject into LLM prompt
        """
        # Get recent call history
        recent_calls = await self.redis.get_recent_calls(user_profile.user_id, limit=3)
        
        context_parts = [
            f"ΧΡΗΣΤΗΣ: {user_profile.preferred_name or user_profile.name}",
            f"ΤΗΛΕΦΩΝΟ: {format_phone_display(user_profile.phone_number)}",
        ]
        
        if user_profile.interests:
            context_parts.append(f"ΕΝΔΙΑΦΕΡΟΝΤΑ: {', '.join(user_profile.interests)}")
        
        if user_profile.favorite_topics:
            context_parts.append(f"ΑΓΑΠΗΜΕΝΑ ΘΕΜΑΤΑ: {', '.join(user_profile.favorite_topics)}")
        
        if user_profile.preferred_greeting:
            context_parts.append(f"ΧΑΙΡΕΤΙΣΜΟΣ: {user_profile.preferred_greeting}")
        
        # Add recent conversation summaries
        if recent_calls:
            context_parts.append("\nΠΡΟΣΦΑΤΕΣ ΣΥΝΟΜΙΛΙΕΣ:")
            for i, call in enumerate(recent_calls, 1):
                if call.summary:
                    date_str = call.timestamp.strftime("%d/%m/%Y")
                    context_parts.append(f"  {i}. [{date_str}] {call.summary}")
        
        return "\n".join(context_parts)


# Global service instance
user_identification_service = UserIdentificationService()
