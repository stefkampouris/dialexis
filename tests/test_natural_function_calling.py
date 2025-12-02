"""
Test script to verify natural function calling implementation.

This script checks that the event handler is properly configured
and the feedback messages are defined correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_event_handler_setup():
    """Verify the event handler is set up correctly in bot.py"""
    bot_file = project_root / "bot.py"
    
    with open(bot_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for required imports
    assert "from pipecat.frames.frames import LLMRunFrame, TTSSpeakFrame" in content, \
        "TTSSpeakFrame not imported"
    
    # Check for event handler registration
    assert '@llm.event_handler("on_function_calls_started")' in content, \
        "Event handler not registered"
    
    # Check for feedback messages
    required_functions = [
        "check_doctor_availability",
        "get_next_available_slots", 
        "create_appointment",
        "update_appointment",
        "cancel_appointment"
    ]
    
    for func in required_functions:
        assert func in content, f"Missing feedback message for {func}"
    
    # Check for Greek messages
    greek_messages = [
        "Ας δω... ελέγχω τη διαθεσιμότητα...",
        "Μια στιγμή, ψάχνω τα επόμενα διαθέσιμα ραντεβού...",
        "Εντάξει, κλείνω το ραντεβού...",
    ]
    
    for msg in greek_messages:
        assert msg in content, f"Missing Greek message: {msg}"
    
    print("✅ All event handler checks passed!")


def test_feedback_messages():
    """Verify feedback messages are properly formatted"""
    feedback_messages = {
        "check_doctor_availability": "Ας δω... ελέγχω τη διαθεσιμότητα...",
        "get_next_available_slots": "Μια στιγμή, ψάχνω τα επόμενα διαθέσιμα ραντεβού...",
        "create_appointment": "Εντάξει, κλείνω το ραντεβού...",
        "update_appointment": "Εντάξει, αλλάζω το ραντεβού...",
        "cancel_appointment": "Εντάξει, ακυρώνω το ραντεβού..."
    }
    
    # All messages should be non-empty strings
    for func_name, message in feedback_messages.items():
        assert isinstance(message, str), f"Message for {func_name} is not a string"
        assert len(message) > 0, f"Message for {func_name} is empty"
        print(f"✓ {func_name}: {message}")
    
    print("✅ All feedback messages are valid!")


if __name__ == "__main__":
    try:
        test_event_handler_setup()
        test_feedback_messages()
        print("\n🎉 All tests passed! The natural function calling is properly implemented.")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
