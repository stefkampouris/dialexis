"""
Function calling tools for the dental secretary agent.

Provides calendar availability checking and appointment management.
"""

from datetime import datetime, timedelta
from typing import Any, Dict
from loguru import logger

from pipecat.services.llm_service import FunctionCallParams
from pipecat.adapters.schemas.function_schema import FunctionSchema
from pipecat.adapters.schemas.tools_schema import ToolsSchema

from src.calendar.google_calendar import calendar_service


# ===================================================================
# FUNCTION DEFINITIONS (for LLM)
# ===================================================================

def create_calendar_tools() -> ToolsSchema:
    """
    Create function schemas for calendar operations.
    
    Returns:
        ToolsSchema with calendar function definitions
    """
    
    # Function 1: Check availability
    check_availability_function = FunctionSchema(
        name="check_doctor_availability",
        description=(
            "Check the dentist's calendar availability for booking appointments. "
            "Returns available and busy time slots. Use this when a patient asks "
            "to book an appointment or wants to know when the doctor is available. "
            "IMPORTANT: You MUST collect patient name and phone number before calling this function."
        ),
        properties={
            "patient_name": {
                "type": "string",
                "description": "Full name of the patient (REQUIRED)"
            },
            "patient_phone": {
                "type": "string",
                "description": "Patient's phone number (REQUIRED)"
            },
            "start_date": {
                "type": "string",
                "description": (
                    "The start date/time to check availability from, in ISO format. "
                    "E.g., '2025-11-16' for a date, or '2025-11-16T09:00:00' for a specific time. "
                    "If the patient says 'αύριο' (tomorrow), 'τη Δευτέρα' (Monday), etc., "
                    "calculate the appropriate date."
                ),
            },
            "end_date": {
                "type": "string",
                "description": (
                    "Optional end date/time for the availability check, in ISO format. "
                    "If not provided, defaults to 7 days from start_date. "
                    "Use this when the patient asks for a specific date range."
                ),
            },
            "preferred_time": {
                "type": "string",
                "description": (
                    "Optional preferred time of day. Values: 'morning' (πρωί), 'afternoon' (απόγευμα), "
                    "'evening' (βράδυ), or a specific time like '14:00'. "
                    "Use this to filter results based on patient preference."
                ),
                "enum": ["morning", "afternoon", "evening", "any"]
            }
        },
        required=["patient_name", "patient_phone", "start_date"]
    )
    
    # Function 2: Get next available slots
    get_next_slots_function = FunctionSchema(
        name="get_next_available_slots",
        description=(
            "Get the next 5 available appointment slots starting from now or a given date. "
            "Use this when a patient asks 'πότε έχει διαθέσιμο;' (when do you have available?) "
            "or 'θέλω το πιο γρήγορο ραντεβού' (I want the earliest appointment). "
            "IMPORTANT: You MUST collect patient name and phone number before calling this function."
        ),
        properties={
            "patient_name": {
                "type": "string",
                "description": "Full name of the patient (REQUIRED)"
            },
            "patient_phone": {
                "type": "string",
                "description": "Patient's phone number (REQUIRED)"
            },
            "from_date": {
                "type": "string",
                "description": (
                    "Optional start date in ISO format (e.g., '2025-11-16'). "
                    "If not provided, starts from today."
                ),
            },
            "count": {
                "type": "integer",
                "description": "Number of slots to return (default: 5, max: 10)",
                "default": 5
            }
        },
        required=["patient_name", "patient_phone"]
    )
    
    # Function 3: Create appointment
    create_appointment_function = FunctionSchema(
        name="create_appointment",
        description=(
            "Create a new dental appointment in the calendar. "
            "Use this after the patient has confirmed they want to book a specific time slot. "
            "IMPORTANT: You MUST have patient name and phone number to create an appointment."
        ),
        properties={
            "patient_name": {
                "type": "string",
                "description": "Full name of the patient (REQUIRED)"
            },
            "patient_phone": {
                "type": "string",
                "description": "Patient's phone number (REQUIRED)"
            },
            "start_datetime": {
                "type": "string",
                "description": "Start date and time in ISO format (e.g., '2025-11-17T09:00:00')"
            },
            "end_datetime": {
                "type": "string",
                "description": "End date and time in ISO format (e.g., '2025-11-17T09:30:00')"
            },
            "appointment_type": {
                "type": "string",
                "description": "Type of appointment: 'καθαρισμός' (cleaning), 'έλεγχος' (checkup), 'θεραπεία' (treatment), 'επείγον' (emergency), etc.",
                "default": "έλεγχος"
            },
            "notes": {
                "type": "string",
                "description": "Optional additional notes about the appointment"
            }
        },
        required=["patient_name", "patient_phone", "start_datetime", "end_datetime"]
    )
    
    # Function 4: Update appointment
    update_appointment_function = FunctionSchema(
        name="update_appointment",
        description=(
            "Update/reschedule an existing appointment. "
            "Use this when a patient wants to change their appointment time or details. "
            "IMPORTANT: You MUST verify patient name and phone number to update an appointment."
        ),
        properties={
            "patient_name": {
                "type": "string",
                "description": "Full name of the patient (REQUIRED for verification)"
            },
            "patient_phone": {
                "type": "string",
                "description": "Patient's phone number (REQUIRED for verification)"
            },
            "event_id": {
                "type": "string",
                "description": "The ID of the appointment to update (obtained from previous queries)"
            },
            "start_datetime": {
                "type": "string",
                "description": "New start date and time in ISO format (optional)"
            },
            "end_datetime": {
                "type": "string",
                "description": "New end date and time in ISO format (optional)"
            },
            "appointment_type": {
                "type": "string",
                "description": "New appointment type (optional)"
            },
            "notes": {
                "type": "string",
                "description": "Updated notes (optional)"
            }
        },
        required=["patient_name", "patient_phone", "event_id"]
    )
    
    # Function 5: Cancel appointment
    cancel_appointment_function = FunctionSchema(
        name="cancel_appointment",
        description=(
            "Cancel/delete an appointment from the calendar. "
            "Use this when a patient wants to cancel their appointment. "
            "IMPORTANT: You MUST verify patient name and phone number before canceling."
        ),
        properties={
            "patient_name": {
                "type": "string",
                "description": "Full name of the patient (REQUIRED for verification)"
            },
            "patient_phone": {
                "type": "string",
                "description": "Patient's phone number (REQUIRED for verification)"
            },
            "event_id": {
                "type": "string",
                "description": "The ID of the appointment to cancel"
            }
        },
        required=["patient_name", "patient_phone", "event_id"]
    )
    
    # Create tools schema
    tools = ToolsSchema(standard_tools=[
        check_availability_function,
        get_next_slots_function,
        create_appointment_function,
        update_appointment_function,
        cancel_appointment_function
    ])
    
    return tools


# ===================================================================
# FUNCTION HANDLERS (implementations)
# ===================================================================

async def handle_check_doctor_availability(params: FunctionCallParams):
    """
    Handler for checking doctor availability.
    
    This is called by the LLM when it needs to check calendar availability.
    """
    try:
        # Extract and validate patient information
        patient_name = params.arguments.get("patient_name")
        patient_phone = params.arguments.get("patient_phone")
        
        if not patient_name or not patient_phone:
            await params.result_callback({
                "success": False,
                "error": "Missing patient information",
                "message": "Μια στιγμή, χρειάζομαι το όνομά σας και τον αριθμό τηλεφώνου σας για να ελέγξω τη διαθεσιμότητα."
            })
            return
        
        # Extract arguments
        start_date = params.arguments.get("start_date")
        end_date = params.arguments.get("end_date")
        preferred_time = params.arguments.get("preferred_time", "any")
        
        # Validate and fix date if needed
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00').split('T')[0])
            now = datetime.now()
            
            # If date is in the past, use today instead
            if start_dt.date() < now.date():
                logger.warning(f"Start date {start_date} is in the past, using today instead")
                start_date = now.strftime('%Y-%m-%d')
        else:
            # No start date provided, use today
            start_date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"📅 Checking availability: {start_date} to {end_date or 'N/A'}")
        
        # Call the calendar service
        availability = calendar_service.get_availability(
            start_date=start_date,
            end_date=end_date,
            timezone="Europe/Athens"
        )
        
        if "error" in availability:
            # Return error to LLM
            await params.result_callback({
                "success": False,
                "error": availability["error"],
                "message": "Λυπάμαι, δεν μπόρεσα να ελέγξω το ημερολόγιο αυτή τη στιγμή."
            })
            return
        
        # Filter by preferred time if specified
        free_slots = availability["free_slots"]
        if preferred_time != "any":
            free_slots = _filter_by_time_preference(free_slots, preferred_time)
        
        # Format response for the LLM
        if not free_slots:
            result = {
                "success": True,
                "has_availability": False,
                "message": "Δεν υπάρχουν διαθέσιμα ραντεβού στο διάστημα που ζητήσατε.",
                "suggestion": "Θα μπορούσα να ελέγξω άλλες ημερομηνίες;"
            }
        else:
            # Format slots in a human-readable way
            formatted_slots = _format_slots_for_llm(free_slots[:10])  # Limit to 10 slots
            
            result = {
                "success": True,
                "has_availability": True,
                "total_slots": len(free_slots),
                "showing_slots": len(formatted_slots),
                "available_slots": formatted_slots,
                "message": f"Υπάρχουν {len(free_slots)} διαθέσιμα ραντεβού."
            }
        
        logger.info(f"✓ Found {len(free_slots)} available slots")
        await params.result_callback(result)
        
    except Exception as e:
        logger.error(f"Error in check_doctor_availability: {e}")
        await params.result_callback({
            "success": False,
            "error": str(e),
            "message": "Συγγνώμη, κάτι πήγε στραβά. Μπορείτε να δοκιμάσετε ξανά;"
        })


async def handle_get_next_available_slots(params: FunctionCallParams):
    """
    Handler for getting next available appointment slots.
    """
    try:
        # Extract and validate patient information
        patient_name = params.arguments.get("patient_name")
        patient_phone = params.arguments.get("patient_phone")
        
        if not patient_name or not patient_phone:
            await params.result_callback({
                "success": False,
                "error": "Missing patient information",
                "message": "Μια στιγμή, χρειάζομαι το όνομά σας και τον αριθμό τηλεφώνου σας για να ελέγξω τα διαθέσιμα ραντεβού."
            })
            return
        
        # Extract arguments
        from_date = params.arguments.get("from_date")
        count = min(params.arguments.get("count", 5), 10)  # Max 10 slots
        
        # Validate and fix date if needed
        if from_date:
            try:
                from_dt = datetime.fromisoformat(from_date.replace('Z', '+00:00').split('T')[0])
                now = datetime.now()
                
                # If date is in the past, use today instead
                if from_dt.date() < now.date():
                    logger.warning(f"From date {from_date} is in the past, using today instead")
                    from_date = now.strftime('%Y-%m-%d')
            except ValueError:
                logger.warning(f"Invalid from_date format: {from_date}, using today")
                from_date = datetime.now().strftime('%Y-%m-%d')
        else:
            # No date provided, start from now
            from_date = datetime.now().strftime('%Y-%m-%d')
        
        # Look ahead 14 days
        end_date = (datetime.fromisoformat(from_date) + timedelta(days=14)).isoformat()
        
        logger.info(f"📅 Getting next {count} available slots from {from_date}")
        
        # Get availability
        availability = calendar_service.get_availability(
            start_date=from_date,
            end_date=end_date,
            timezone="Europe/Athens"
        )
        
        if "error" in availability:
            await params.result_callback({
                "success": False,
                "error": availability["error"],
                "message": "Δεν μπόρεσα να ελέγξω τη διαθεσιμότητα αυτή τη στιγμή."
            })
            return
        
        # Get first N slots
        free_slots = availability["free_slots"][:count]
        
        if not free_slots:
            result = {
                "success": True,
                "has_availability": False,
                "message": "Δεν υπάρχουν διαθέσιμα ραντεβού τις επόμενες 2 εβδομάδες.",
                "suggestion": "Θέλετε να ελέγξω πιο μακριά στο μέλλον;"
            }
        else:
            formatted_slots = _format_slots_for_llm(free_slots)
            
            result = {
                "success": True,
                "has_availability": True,
                "next_available": formatted_slots[0] if formatted_slots else None,
                "all_slots": formatted_slots,
                "message": f"Το επόμενο διαθέσιμο ραντεβού είναι: {formatted_slots[0]['readable']}"
            }
        
        logger.info(f"✓ Returning {len(free_slots)} next available slots")
        await params.result_callback(result)
        
    except Exception as e:
        logger.error(f"Error in get_next_available_slots: {e}")
        await params.result_callback({
            "success": False,
            "error": str(e),
            "message": "Λυπάμαι, κάτι πήγε στραβά."
        })


async def handle_create_appointment(params: FunctionCallParams):
    """
    Handler for creating a new appointment.
    """
    try:
        # Extract and validate patient information
        patient_name = params.arguments.get("patient_name")
        patient_phone = params.arguments.get("patient_phone")
        
        if not patient_name or not patient_phone:
            await params.result_callback({
                "success": False,
                "error": "Missing patient information",
                "message": "Μια στιγμή, χρειάζομαι το όνομά σας και τον αριθμό τηλεφώνου σας για να δημιουργήσω το ραντεβού."
            })
            return
        
        # Extract arguments
        start_datetime = params.arguments.get("start_datetime")
        end_datetime = params.arguments.get("end_datetime")
        appointment_type = params.arguments.get("appointment_type", "έλεγχος")
        notes = params.arguments.get("notes", "")
        
        logger.info(f"📝 Creating appointment for {patient_name} at {start_datetime}")
        
        # Create the appointment
        result = calendar_service.create_event(
            summary=f"{appointment_type} - {patient_name}",
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            description=notes,
            patient_name=patient_name,
            patient_phone=patient_phone,
            timezone="Europe/Athens"
        )
        
        if "error" in result:
            await params.result_callback({
                "success": False,
                "error": result["error"],
                "message": "Λυπάμαι, δεν μπόρεσα να δημιουργήσω το ραντεβού."
            })
            return
        
        # Format success message
        from datetime import datetime
        start_dt = datetime.fromisoformat(start_datetime)
        day_name = ["Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη", "Παρασκευή", "Σάββατο", "Κυριακή"][start_dt.weekday()]
        time_str = start_dt.strftime("%H:%M")
        
        await params.result_callback({
            "success": True,
            "event_id": result["event_id"],
            "message": f"Εντάξει! Το ραντεβού σας έχει κλειστεί για {day_name}, {start_dt.day} {start_dt.strftime('%B')} στις {time_str}. Σας περιμένουμε!"
        })
        
        logger.info(f"✓ Appointment created: {result['event_id']}")
        
    except Exception as e:
        logger.error(f"Error in create_appointment: {e}")
        await params.result_callback({
            "success": False,
            "error": str(e),
            "message": "Λυπάμαι, κάτι πήγε στραβά με τη δημιουργία του ραντεβού."
        })


async def handle_update_appointment(params: FunctionCallParams):
    """
    Handler for updating an existing appointment.
    """
    try:
        # Extract and validate patient information
        patient_name = params.arguments.get("patient_name")
        patient_phone = params.arguments.get("patient_phone")
        
        if not patient_name or not patient_phone:
            await params.result_callback({
                "success": False,
                "error": "Missing patient information",
                "message": "Μια στιγμή, χρειάζομαι το όνομά σας και τον αριθμό τηλεφώνου σας για να ενημερώσω το ραντεβού."
            })
            return
        
        # Extract arguments
        event_id = params.arguments.get("event_id")
        start_datetime = params.arguments.get("start_datetime")
        end_datetime = params.arguments.get("end_datetime")
        appointment_type = params.arguments.get("appointment_type")
        notes = params.arguments.get("notes")
        
        logger.info(f"✏️ Updating appointment {event_id}")
        
        # Build summary if appointment type is provided
        summary = f"{appointment_type}" if appointment_type else None
        
        # Update the appointment
        result = calendar_service.update_event(
            event_id=event_id,
            summary=summary,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            description=notes,
            timezone="Europe/Athens"
        )
        
        if "error" in result:
            await params.result_callback({
                "success": False,
                "error": result["error"],
                "message": "Λυπάμαι, δεν μπόρεσα να ενημερώσω το ραντεβού. Ίσως έχει ακυρωθεί ή δεν υπάρχει πλέον."
            })
            return
        
        await params.result_callback({
            "success": True,
            "event_id": result["event_id"],
            "message": "Το ραντεβού σας έχει ενημερωθεί επιτυχώς!"
        })
        
        logger.info(f"✓ Appointment updated: {event_id}")
        
    except Exception as e:
        logger.error(f"Error in update_appointment: {e}")
        await params.result_callback({
            "success": False,
            "error": str(e),
            "message": "Λυπάμαι, κάτι πήγε στραβά με την ενημέρωση του ραντεβού."
        })


async def handle_cancel_appointment(params: FunctionCallParams):
    """
    Handler for canceling an appointment.
    """
    try:
        # Extract and validate patient information
        patient_name = params.arguments.get("patient_name")
        patient_phone = params.arguments.get("patient_phone")
        
        if not patient_name or not patient_phone:
            await params.result_callback({
                "success": False,
                "error": "Missing patient information",
                "message": "Μια στιγμή, χρειάζομαι το όνομά σας και τον αριθμό τηλεφώνου σας για να ακυρώσω το ραντεβού."
            })
            return
        
        # Extract arguments
        event_id = params.arguments.get("event_id")
        
        logger.info(f"🗑️ Canceling appointment {event_id}")
        
        # Delete the appointment
        result = calendar_service.delete_event(event_id)
        
        if "error" in result:
            await params.result_callback({
                "success": False,
                "error": result["error"],
                "message": "Λυπάμαι, δεν μπόρεσα να ακυρώσω το ραντεβού. Ίσως έχει ήδη ακυρωθεί."
            })
            return
        
        await params.result_callback({
            "success": True,
            "event_id": event_id,
            "message": "Το ραντεβού σας έχει ακυρωθεί επιτυχώς. Ελπίζουμε να σας δούμε σύντομα!"
        })
        
        logger.info(f"✓ Appointment canceled: {event_id}")
        
    except Exception as e:
        logger.error(f"Error in cancel_appointment: {e}")
        await params.result_callback({
            "success": False,
            "error": str(e),
            "message": "Λυπάμαι, κάτι πήγε στραβά με την ακύρωση του ραντεβού."
        })


# ===================================================================
# HELPER FUNCTIONS
# ===================================================================

def _filter_by_time_preference(slots: list, preference: str) -> list:
    """Filter slots based on time preference."""
    if preference == "any":
        return slots
    
    filtered = []
    for slot in slots:
        start_time = datetime.fromisoformat(slot["start"])
        hour = start_time.hour
        
        if preference == "morning" and 9 <= hour < 12:
            filtered.append(slot)
        elif preference == "afternoon" and 12 <= hour < 17:
            filtered.append(slot)
        elif preference == "evening" and 17 <= hour < 20:
            filtered.append(slot)
    
    return filtered


def _format_slots_for_llm(slots: list) -> list:
    """Format slots in a human-readable way for the LLM."""
    formatted = []
    
    # Greek day names
    day_names = {
        0: "Δευτέρα",
        1: "Τρίτη",
        2: "Τετάρτη",
        3: "Πέμπτη",
        4: "Παρασκευή",
        5: "Σάββατο",
        6: "Κυριακή"
    }
    
    for slot in slots:
        start_dt = datetime.fromisoformat(slot["start"])
        end_dt = datetime.fromisoformat(slot["end"])
        
        day_name = day_names[start_dt.weekday()]
        date_str = start_dt.strftime("%d/%m/%Y")
        time_str = start_dt.strftime("%H:%M")
        end_time_str = end_dt.strftime("%H:%M")
        
        formatted.append({
            "start": slot["start"],
            "end": slot["end"],
            "duration": slot["duration_minutes"],
            "readable": f"{day_name} {date_str} στις {time_str}",
            "day": day_name,
            "date": date_str,
            "time": time_str,
            "end_time": end_time_str
        })
    
    return formatted


def register_calendar_functions(llm_service):
    """
    Register all calendar function handlers with the LLM service.
    
    Args:
        llm_service: The LLM service instance (OpenAI, Azure, etc.)
    """
    logger.info("Registering calendar function handlers...")
    
    # Register function handlers
    llm_service.register_function(
        "check_doctor_availability",
        handle_check_doctor_availability,
        cancel_on_interruption=False  # Don't cancel calendar checks on interruption
    )
    
    llm_service.register_function(
        "get_next_available_slots",
        handle_get_next_available_slots,
        cancel_on_interruption=False
    )
    
    llm_service.register_function(
        "create_appointment",
        handle_create_appointment,
        cancel_on_interruption=False
    )
    
    llm_service.register_function(
        "update_appointment",
        handle_update_appointment,
        cancel_on_interruption=False
    )
    
    llm_service.register_function(
        "cancel_appointment",
        handle_cancel_appointment,
        cancel_on_interruption=False
    )
    
    logger.info("✓ Calendar functions registered")
