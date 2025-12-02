"""
Phone number utilities
Validates and normalizes phone numbers (primarily Greek numbers)
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def normalize_phone_number(phone: str) -> Optional[str]:
    """
    Normalize a phone number to E.164 format
    Primarily handles Greek phone numbers (+30)
    
    Args:
        phone: Phone number in various formats
    
    Returns:
        Normalized phone number in E.164 format (+30xxxxxxxxxx) or None if invalid
    
    Examples:
        "6912345678" -> "+306912345678"
        "0030 691 234 5678" -> "+306912345678"
        "+30 691-234-5678" -> "+306912345678"
        "2103456789" -> "+302103456789" (landline)
    """
    if not phone:
        return None
    
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Handle different formats
    if cleaned.startswith('+30'):
        # Already in E.164 format with +30
        number = cleaned
    elif cleaned.startswith('0030'):
        # Replace 0030 with +30
        number = '+30' + cleaned[4:]
    elif cleaned.startswith('30'):
        # Add + prefix
        number = '+' + cleaned
    elif cleaned.startswith('0') and len(cleaned) == 11:
        # Greek format with leading 0 (e.g., 06912345678)
        number = '+30' + cleaned[1:]
    elif len(cleaned) == 10:
        # Greek format without country code (e.g., 6912345678)
        number = '+30' + cleaned
    else:
        # Unknown format
        logger.warning(f"Unable to normalize phone number: {phone}")
        return None
    
    # Validate Greek phone number format
    if validate_greek_phone_number(number):
        return number
    else:
        logger.warning(f"Invalid Greek phone number after normalization: {number}")
        return None


def validate_greek_phone_number(phone: str) -> bool:
    """
    Validate a Greek phone number in E.164 format
    
    Args:
        phone: Phone number in E.164 format (+30xxxxxxxxxx)
    
    Returns:
        True if valid, False otherwise
    
    Valid formats:
        Mobile: +306xxxxxxxxx (10 digits after +30, starting with 6)
        Landline: +302xxxxxxxxx (10 digits after +30, starting with 2)
    """
    if not phone:
        return False
    
    # Check E.164 format with +30
    if not phone.startswith('+30'):
        return False
    
    # Extract digits after +30
    digits = phone[3:]
    
    # Must be exactly 10 digits
    if len(digits) != 10:
        return False
    
    # Must be all digits
    if not digits.isdigit():
        return False
    
    # First digit must be 2 (landline) or 6 (mobile)
    if digits[0] not in ['2', '6']:
        return False
    
    return True


def format_phone_display(phone: str) -> str:
    """
    Format phone number for display
    
    Args:
        phone: Phone number in E.164 format
    
    Returns:
        Formatted phone number for display
    
    Example:
        "+306912345678" -> "+30 691 234 5678"
        "+302103456789" -> "+30 210 345 6789"
    """
    if not phone or not phone.startswith('+30'):
        return phone
    
    digits = phone[3:]
    if len(digits) != 10:
        return phone
    
    # Format: +30 XXX XXX XXXX
    return f"+30 {digits[:3]} {digits[3:6]} {digits[6:]}"


def is_mobile_number(phone: str) -> bool:
    """
    Check if phone number is a mobile number
    
    Args:
        phone: Phone number in E.164 format
    
    Returns:
        True if mobile, False otherwise
    """
    if not phone or not phone.startswith('+30'):
        return False
    
    digits = phone[3:]
    return len(digits) == 10 and digits[0] == '6'


def validate_mobile_only(phone: str) -> bool:
    """
    Validate that phone number is a Greek mobile (starts with 69)
    
    Args:
        phone: Phone number in any format
    
    Returns:
        True if valid Greek mobile starting with 69, False otherwise
    """
    normalized = normalize_phone_number(phone)
    if not normalized:
        return False
    
    # Must be mobile (+306...)
    if not is_mobile_number(normalized):
        return False
    
    # Must start with 69 (after +30)
    digits = normalized[3:]
    return digits.startswith('69')


def is_landline_number(phone: str) -> bool:
    """
    Check if phone number is a landline number
    
    Args:
        phone: Phone number in E.164 format
    
    Returns:
        True if landline, False otherwise
    """
    if not phone or not phone.startswith('+30'):
        return False
    
    digits = phone[3:]
    return len(digits) == 10 and digits[0] == '2'


# Test function for development
def test_phone_normalization():
    """Test phone number normalization"""
    test_cases = [
        ("6912345678", "+306912345678"),
        ("0030 691 234 5678", "+306912345678"),
        ("+30 691-234-5678", "+306912345678"),
        ("06912345678", "+306912345678"),
        ("2103456789", "+302103456789"),
        ("+30 210 345 6789", "+302103456789"),
        ("invalid", None),
        ("123", None),
    ]
    
    print("Testing phone number normalization:")
    for input_phone, expected in test_cases:
        result = normalize_phone_number(input_phone)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {input_phone:20} -> {result} (expected: {expected})")


if __name__ == "__main__":
    test_phone_normalization()
