"""
Test script for user identification system
Tests phone number validation, user registration, and Redis operations
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.database.redis_client import redis_client
from src.users.identification import user_identification_service
from src.utils.phone_numbers import (
    normalize_phone_number,
    validate_greek_phone_number,
    format_phone_display,
    is_mobile_number,
    is_landline_number
)


async def test_phone_normalization():
    """Test phone number normalization"""
    print("\n" + "="*60)
    print("TEST 1: Phone Number Normalization")
    print("="*60)
    
    test_cases = [
        ("6912345678", "+306912345678", True),
        ("0030 691 234 5678", "+306912345678", True),
        ("+30 691-234-5678", "+306912345678", True),
        ("06912345678", "+306912345678", True),
        ("2103456789", "+302103456789", True),
        ("+30 210 345 6789", "+302103456789", True),
        ("invalid", None, False),
        ("123", None, False),
    ]
    
    passed = 0
    failed = 0
    
    for input_phone, expected, should_pass in test_cases:
        result = normalize_phone_number(input_phone)
        
        if should_pass:
            if result == expected:
                print(f"  ✓ {input_phone:20} -> {result}")
                passed += 1
            else:
                print(f"  ✗ {input_phone:20} -> {result} (expected: {expected})")
                failed += 1
        else:
            if result is None:
                print(f"  ✓ {input_phone:20} -> None (correctly rejected)")
                passed += 1
            else:
                print(f"  ✗ {input_phone:20} -> {result} (should be None)")
                failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


async def test_redis_connection():
    """Test Redis connection"""
    print("\n" + "="*60)
    print("TEST 2: Redis Connection")
    print("="*60)
    
    try:
        await redis_client.initialize()
        print("  ✓ Redis client initialized successfully")
        
        # Test basic operation
        total_users = await redis_client.get_total_users()
        print(f"  ✓ Total users in database: {total_users}")
        
        return True
    except Exception as e:
        print(f"  ✗ Redis connection failed: {e}")
        return False


async def test_user_registration():
    """Test user registration and retrieval"""
    print("\n" + "="*60)
    print("TEST 3: User Registration & Retrieval")
    print("="*60)
    
    # Test data
    test_phone = "+306912345678"
    test_name = "Μαρία Παπαδοπούλου"
    test_preferred_name = "κυρία Μαρία"
    
    try:
        # Check if user exists
        user_profile, is_new = await user_identification_service.identify_user(test_phone)
        
        if user_profile:
            print(f"  ℹ User already exists: {user_profile.name}")
            print(f"    - User ID: {user_profile.user_id}")
            print(f"    - Phone: {format_phone_display(user_profile.phone_number)}")
            print(f"    - Preferred Name: {user_profile.preferred_name}")
            return True
        
        # Register new user
        print(f"  ℹ Registering new user: {test_name}")
        user_profile = await user_identification_service.register_new_user(
            phone_number=test_phone,
            name=test_name,
            preferred_name=test_preferred_name
        )
        
        if not user_profile:
            print(f"  ✗ Failed to register user")
            return False
        
        print(f"  ✓ User registered successfully")
        print(f"    - User ID: {user_profile.user_id}")
        print(f"    - Phone: {format_phone_display(user_profile.phone_number)}")
        print(f"    - Name: {user_profile.name}")
        print(f"    - Preferred Name: {user_profile.preferred_name}")
        
        # Try to retrieve the user
        print(f"\n  ℹ Retrieving user by phone number...")
        retrieved_user, is_new = await user_identification_service.identify_user(test_phone)
        
        if not retrieved_user:
            print(f"  ✗ Failed to retrieve user")
            return False
        
        print(f"  ✓ User retrieved successfully")
        print(f"    - Name matches: {retrieved_user.name == test_name}")
        print(f"    - Phone matches: {retrieved_user.phone_number == test_phone}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error during user registration test: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_user_preferences():
    """Test updating user preferences"""
    print("\n" + "="*60)
    print("TEST 4: User Preferences Update")
    print("="*60)
    
    test_phone = "+306912345678"
    
    try:
        # Get user
        user_profile, _ = await user_identification_service.identify_user(test_phone)
        
        if not user_profile:
            print(f"  ✗ User not found")
            return False
        
        print(f"  ℹ Updating preferences for {user_profile.name}")
        
        # Update preferences
        success = await user_identification_service.update_user_preferences(
            user_id=user_profile.user_id,
            interests=["εκκλησία", "χειροτεχνία", "μουσική"],
            favorite_topics=["εγγόνια", "κήπος", "μαγειρική"],
            preferred_greeting="Καλημέρα κυρία Μαρία"
        )
        
        if not success:
            print(f"  ✗ Failed to update preferences")
            return False
        
        print(f"  ✓ Preferences updated successfully")
        
        # Retrieve updated user
        updated_user, _ = await user_identification_service.identify_user(test_phone)
        
        print(f"  ✓ Updated interests: {', '.join(updated_user.interests)}")
        print(f"  ✓ Updated favorite topics: {', '.join(updated_user.favorite_topics)}")
        print(f"  ✓ Updated greeting: {updated_user.preferred_greeting}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error during preferences test: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_user_context_generation():
    """Test generating user context for LLM"""
    print("\n" + "="*60)
    print("TEST 5: User Context Generation")
    print("="*60)
    
    test_phone = "+306912345678"
    
    try:
        # Get user
        user_profile, _ = await user_identification_service.identify_user(test_phone)
        
        if not user_profile:
            print(f"  ✗ User not found")
            return False
        
        # Generate context
        context = await user_identification_service.generate_user_context(user_profile)
        
        print(f"  ✓ Generated user context:\n")
        print("  " + "\n  ".join(context.split("\n")))
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error during context generation test: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_all_users():
    """List all users in database"""
    print("\n" + "="*60)
    print("TEST 6: List All Users")
    print("="*60)
    
    try:
        total_users = await redis_client.get_total_users()
        print(f"  ℹ Total users: {total_users}")
        
        user_ids = await redis_client.get_all_user_ids()
        
        for user_id in user_ids:
            user = await redis_client.get_user_profile(user_id)
            if user:
                print(f"\n  User: {user.name}")
                print(f"    - ID: {user.user_id}")
                print(f"    - Phone: {format_phone_display(user.phone_number)}")
                print(f"    - Status: {user.status}")
                print(f"    - Registered: {user.registration_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error listing users: {e}")
        return False


async def main():
    """Run all tests"""
    print("\n")
    print("="*60)
    print("NINIKO USER IDENTIFICATION SYSTEM - TEST SUITE")
    print("="*60)
    
    # Check configuration
    print("\nConfiguration Check:")
    print(f"  Redis URL: {'✓' if os.getenv('UPSTASH_REDIS_REST_URL') else '✗ MISSING'}")
    print(f"  Redis Token: {'✓' if os.getenv('UPSTASH_REDIS_REST_TOKEN') else '✗ MISSING'}")
    
    if not os.getenv('UPSTASH_REDIS_REST_URL') or not os.getenv('UPSTASH_REDIS_REST_TOKEN'):
        print("\n⚠️  Please set UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN in .env file")
        return
    
    # Run tests
    results = []
    
    # Test 1: Phone normalization (no async needed)
    results.append(("Phone Normalization", await test_phone_normalization()))
    
    # Test 2: Redis connection
    results.append(("Redis Connection", await test_redis_connection()))
    
    # Test 3: User registration
    results.append(("User Registration", await test_user_registration()))
    
    # Test 4: User preferences
    results.append(("User Preferences", await test_user_preferences()))
    
    # Test 5: Context generation
    results.append(("Context Generation", await test_user_context_generation()))
    
    # Test 6: List all users
    results.append(("List All Users", await test_all_users()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status:8} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    # Close Redis connection
    await redis_client.close()


if __name__ == "__main__":
    asyncio.run(main())
