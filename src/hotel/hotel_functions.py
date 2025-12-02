"""
Function calling tools for the Hotel AI Receptionist.

Provides function schemas and handlers for:
- Hotel information queries
- Check-in/check-out policy inquiries
- Room information and comparisons
- Facility information and availability
"""

from typing import Any, Dict
from loguru import logger

from pipecat.services.llm_service import FunctionCallParams
from pipecat.adapters.schemas.function_schema import FunctionSchema
from pipecat.adapters.schemas.tools_schema import ToolsSchema

from src.hotel.hotel_knowledge import get_knowledge_base


# ===================================================================
# FUNCTION SCHEMAS
# ===================================================================

def create_hotel_tools() -> ToolsSchema:
    """
    Create function schemas for hotel operations.
    
    Returns:
        ToolsSchema with hotel function definitions for Phase 1
    """
    
    # Function 1: Get Hotel Information
    get_hotel_info_schema = FunctionSchema(
        name="get_hotel_information",
        description=(
            "Retrieve general information about the hotel including name, location, "
            "contact details, star rating, description, awards, and certifications. "
            "Use this when guest asks: 'Tell me about the hotel', 'What's your address?', "
            "'How can I contact you?', 'What awards have you won?'"
        ),
        properties={
            "info_type": {
                "type": "string",
                "description": "Type of information requested",
                "enum": ["overview", "contact", "location", "awards", "all"]
            }
        },
        required=[]
    )
    
    # Function 2: Get Check-in/Check-out Information
    get_checkin_checkout_schema = FunctionSchema(
        name="get_checkin_checkout_info",
        description=(
            "Get information about check-in and check-out policies including standard times, "
            "early/late options with fees, required documents, and deposit information. "
            "Use when guest asks: 'What time is check-in?', 'Can I check in early?', "
            "'What time do I need to check out?', 'Is there a fee for late checkout?', "
            "'What do I need to bring?', 'Do you require a deposit?'"
        ),
        properties={
            "query_type": {
                "type": "string",
                "description": "Specific query about check-in/out",
                "enum": ["checkin_time", "checkout_time", "early_checkin", 
                         "late_checkout", "requirements", "deposits", "all"]
            },
            "requested_time": {
                "type": "string",
                "description": "Optional: specific time guest wants to check in/out (HH:MM format)"
            }
        },
        required=["query_type"]
    )
    
    # Function 3: Get Room Information
    get_room_info_schema = FunctionSchema(
        name="get_room_information",
        description=(
            "Get detailed information about room types, features, amenities, bed configurations, "
            "views, capacity, and pricing. Use when guest asks about: 'What room types do you have?', "
            "'Tell me about your suites', 'Do you have rooms with two beds?', "
            "'What's in the room?', 'What amenities are included?', "
            "'What's the difference between deluxe and standard?', 'Do you have ocean view rooms?'"
        ),
        properties={
            "room_category": {
                "type": "string",
                "description": "Category of room to query (leave empty for all)",
                "enum": ["all", "standard", "deluxe", "suite", "family", "accessible"]
            },
            "specific_query": {
                "type": "string",
                "description": "Specific aspect of rooms being asked about",
                "enum": ["overview", "amenities", "bed_config", "views", 
                         "capacity", "comparison", "pricing"]
            },
            "filter_criteria": {
                "type": "object",
                "description": "Optional filters for room search",
                "properties": {
                    "min_occupancy": {
                        "type": "integer",
                        "description": "Minimum number of guests"
                    },
                    "view_type": {
                        "type": "string",
                        "description": "Desired view type (ocean, city, garden, etc.)"
                    }
                }
            }
        },
        required=["specific_query"]
    )
    
    # Function 4: Get Facility Information
    get_facility_info_schema = FunctionSchema(
        name="get_facility_information",
        description=(
            "Get information about hotel facilities including restaurants, bars, pools, gym, spa, "
            "business center and other amenities. Includes operating hours, location, pricing, "
            "reservation requirements, and features. Use when guest asks: 'Do you have a gym?', "
            "'Tell me about your restaurant', 'What time does the pool open?', "
            "'Do you have a spa?', 'What facilities do you have?', 'Is breakfast included?'"
        ),
        properties={
            "facility_category": {
                "type": "string",
                "description": "Category of facility (leave empty to search all)",
                "enum": ["all", "dining", "recreation", "wellness", "business", "services"]
            },
            "facility_name": {
                "type": "string",
                "description": "Specific facility name or keyword to search for (e.g., 'restaurant', 'pool', 'gym')"
            },
            "query_aspect": {
                "type": "string",
                "description": "Specific aspect being asked about",
                "enum": ["overview", "hours", "pricing", "amenities", "booking", "location", "all"]
            }
        },
        required=["query_aspect"]
    )
    
    # Create tools schema
    tools = ToolsSchema(standard_tools=[
        get_hotel_info_schema,
        get_checkin_checkout_schema,
        get_room_info_schema,
        get_facility_info_schema,
    ])
    
    return tools


# ===================================================================
# FUNCTION HANDLERS
# ===================================================================

async def handle_get_hotel_information(params: FunctionCallParams):
    """
    Handler for hotel information queries.
    
    Retrieves general hotel information based on requested info type.
    """
    try:
        info_type = params.arguments.get("info_type", "overview")
        
        kb = get_knowledge_base()
        if not kb:
            await params.result_callback({
                "success": False,
                "error": "Knowledge base not initialized",
                "message": "I apologize, I'm having trouble accessing hotel information right now."
            })
            return
        
        hotel_info = kb.get_hotel_info()
        if not hotel_info:
            await params.result_callback({
                "success": False,
                "error": "Hotel info not found",
                "message": "I apologize, hotel information is not available at the moment."
            })
            return
        
        logger.info(f"🏨 Getting hotel info: {info_type}")
        
        # Build response based on info type
        result = {"success": True}
        
        if info_type in ["overview", "all"]:
            result["hotel_name"] = hotel_info.name
            result["star_rating"] = hotel_info.star_rating
            result["description"] = hotel_info.description
            result["tagline"] = hotel_info.tagline
            if hotel_info.brand:
                result["brand"] = hotel_info.brand
        
        if info_type in ["contact", "all"]:
            result["phone"] = hotel_info.contact.phone_main
            result["phone_reservations"] = hotel_info.contact.phone_reservations
            result["email"] = hotel_info.contact.email_main
            result["website"] = hotel_info.contact.website
        
        if info_type in ["location", "all"]:
            result["address"] = hotel_info.get_full_address()
            result["city"] = hotel_info.address.city
            result["region"] = hotel_info.address.region
            result["country"] = hotel_info.address.country
            if hotel_info.address.directions:
                result["directions"] = hotel_info.address.directions
        
        if info_type in ["awards", "all"]:
            result["awards"] = hotel_info.awards
            result["certifications"] = hotel_info.certifications
        
        await params.result_callback(result)
        logger.info(f"✓ Provided hotel {info_type} information")
        
    except Exception as e:
        logger.error(f"Error in get_hotel_information: {e}")
        await params.result_callback({
            "success": False,
            "error": str(e),
            "message": "I apologize, I encountered an error retrieving that information."
        })


async def handle_get_checkin_checkout_info(params: FunctionCallParams):
    """
    Handler for check-in/check-out policy inquiries.
    
    Provides information about check-in/out times, early/late options, fees,
    requirements, and deposits.
    """
    try:
        query_type = params.arguments.get("query_type", "all")
        requested_time = params.arguments.get("requested_time")
        
        kb = get_knowledge_base()
        if not kb:
            await params.result_callback({
                "success": False,
                "error": "Knowledge base not initialized"
            })
            return
        
        checkin_info = kb.get_checkin_info()
        checkout_info = kb.get_checkout_info()
        
        logger.info(f"🕐 Getting check-in/out info: {query_type}")
        
        result = {"success": True}
        
        # Handle check-in queries
        if query_type in ["checkin_time", "early_checkin", "all"]:
            result["standard_checkin"] = checkin_info.get("time")
            result["early_checkin_available"] = checkin_info.get("early_available")
            
            if checkin_info.get("early_available"):
                result["early_checkin_fee"] = checkin_info.get("early_fee")
                result["early_checkin_guaranteed_time"] = checkin_info.get("early_guaranteed_time")
        
        # Handle check-out queries
        if query_type in ["checkout_time", "late_checkout", "all"]:
            result["standard_checkout"] = checkout_info.get("time")
            result["late_checkout_available"] = checkout_info.get("late_available")
            
            if checkout_info.get("late_available"):
                result["late_checkout_fee"] = checkout_info.get("late_fee")
                result["late_checkout_latest_time"] = checkout_info.get("late_latest_time")
        
        # Handle requirements
        if query_type in ["requirements", "all"]:
            result["requirements"] = checkin_info.get("requirements", [])
        
        # Handle deposits
        if query_type in ["deposits", "all"]:
            result["deposit_required"] = checkin_info.get("deposit_required")
            result["deposit_amount"] = checkin_info.get("deposit_amount")
        
        # If guest asked about specific time, provide guidance
        if requested_time:
            result["requested_time"] = requested_time
            result["needs_early_checkin"] = requested_time < checkin_info.get("time", "15:00")
            result["needs_late_checkout"] = requested_time > checkout_info.get("time", "11:00")
        
        await params.result_callback(result)
        logger.info(f"✓ Provided check-in/out information")
        
    except Exception as e:
        logger.error(f"Error in get_checkin_checkout_info: {e}")
        await params.result_callback({
            "success": False,
            "error": str(e)
        })


async def handle_get_room_information(params: FunctionCallParams):
    """
    Handler for room information queries.
    
    Provides detailed room information including types, amenities,
    configurations, and comparisons.
    """
    try:
        room_category = params.arguments.get("room_category", "all")
        specific_query = params.arguments.get("specific_query")
        filter_criteria = params.arguments.get("filter_criteria", {})
        
        kb = get_knowledge_base()
        if not kb:
            await params.result_callback({
                "success": False,
                "error": "Knowledge base not initialized"
            })
            return
        
        logger.info(f"🛏️  Getting room info: category={room_category}, query={specific_query}")
        
        # Build filters
        filters = {}
        if room_category != "all":
            filters["category"] = room_category
        if "min_occupancy" in filter_criteria:
            filters["min_occupancy"] = filter_criteria["min_occupancy"]
        if "view_type" in filter_criteria:
            filters["view_type"] = filter_criteria["view_type"]
        
        # Get rooms
        rooms = kb.get_room_types(filters=filters if filters else None)
        
        if not rooms:
            await params.result_callback({
                "success": True,
                "has_rooms": False,
                "message": "I apologize, I don't have information about rooms matching those criteria."
            })
            return
        
        result = {"success": True, "has_rooms": True, "room_count": len(rooms)}
        
        # Handle different query types
        if specific_query == "overview":
            result["rooms"] = [
                {
                    "id": room.room_type_id,
                    "name": room.name,
                    "category": room.category,
                    "description": room.description,
                    "size_sqm": room.size_sqm,
                    "max_occupancy": room.max_occupancy,
                    "beds": room.get_bed_description(),
                    "views": room.view_types,
                    "base_rate": room.base_rate
                }
                for room in rooms
            ]
        
        elif specific_query == "amenities":
            result["rooms"] = [
                {
                    "name": room.name,
                    "wifi": room.amenities.wifi.dict(),
                    "tv": room.amenities.tv.dict(),
                    "climate_control": room.amenities.climate_control,
                    "minibar": room.amenities.minibar,
                    "coffee_tea": room.amenities.coffee_tea,
                    "safe": room.amenities.safe,
                    "workspace": room.amenities.workspace,
                    "balcony": room.amenities.balcony,
                    "bathroom": room.amenities.bathroom.dict()
                }
                for room in rooms
            ]
        
        elif specific_query == "bed_config":
            result["rooms"] = [
                {
                    "name": room.name,
                    "bed_description": room.get_bed_description(),
                    "bed_details": [
                        {"type": bed.bed_type, "quantity": bed.quantity}
                        for bed in room.bed_configuration
                    ]
                }
                for room in rooms
            ]
        
        elif specific_query == "views":
            result["rooms"] = [
                {
                    "name": room.name,
                    "available_views": room.view_types,
                    "floor_range": room.floor_range
                }
                for room in rooms
            ]
        
        elif specific_query == "comparison" and len(rooms) > 1:
            # Compare rooms
            comparison = kb.compare_rooms([r.room_type_id for r in rooms])
            result["comparison"] = comparison
        
        elif specific_query == "pricing":
            result["rooms"] = [
                {
                    "name": room.name,
                    "category": room.category,
                    "base_rate": room.base_rate,
                    "size_sqm": room.size_sqm,
                    "max_occupancy": room.max_occupancy
                }
                for room in rooms
            ]
        
        await params.result_callback(result)
        logger.info(f"✓ Provided info for {len(rooms)} rooms")
        
    except Exception as e:
        logger.error(f"Error in get_room_information: {e}")
        await params.result_callback({
            "success": False,
            "error": str(e)
        })


async def handle_get_facility_information(params: FunctionCallParams):
    """
    Handler for facility information queries.
    
    Provides information about hotel facilities including operating hours,
    location, amenities, and reservation requirements.
    """
    try:
        category = params.arguments.get("facility_category", "all")
        facility_name = params.arguments.get("facility_name")
        query_aspect = params.arguments.get("query_aspect")
        
        kb = get_knowledge_base()
        if not kb:
            await params.result_callback({
                "success": False,
                "error": "Knowledge base not initialized"
            })
            return
        
        logger.info(f"🏊 Getting facility info: category={category}, name={facility_name}, aspect={query_aspect}")
        
        # Get facilities
        if facility_name:
            facilities = kb.search_facilities(facility_name)
        elif category != "all":
            facilities = kb.get_facilities_by_category(category)
        else:
            facilities = kb.get_all_facilities()
        
        if not facilities:
            await params.result_callback({
                "success": True,
                "has_facilities": False,
                "message": "I apologize, I couldn't find information about that facility."
            })
            return
        
        result = {
            "success": True,
            "has_facilities": True,
            "facility_count": len(facilities)
        }
        
        # Format response based on query aspect
        if query_aspect in ["overview", "all"]:
            result["facilities"] = [
                {
                    "name": f.name,
                    "category": f.category,
                    "description": f.description,
                    "location": f.location,
                    "reservation_required": f.reservation_required
                }
                for f in facilities
            ]
        
        if query_aspect in ["hours", "all"]:
            result["operating_hours"] = [
                {
                    "name": f.name,
                    "hours": {
                        "monday": str(f.operating_hours.monday) if f.operating_hours.monday else "Closed",
                        "tuesday": str(f.operating_hours.tuesday) if f.operating_hours.tuesday else "Closed",
                        "wednesday": str(f.operating_hours.wednesday) if f.operating_hours.wednesday else "Closed",
                        "thursday": str(f.operating_hours.thursday) if f.operating_hours.thursday else "Closed",
                        "friday": str(f.operating_hours.friday) if f.operating_hours.friday else "Closed",
                        "saturday": str(f.operating_hours.saturday) if f.operating_hours.saturday else "Closed",
                        "sunday": str(f.operating_hours.sunday) if f.operating_hours.sunday else "Closed",
                    },
                    "seasonal": f.operating_hours.seasonal,
                    "notes": f.operating_hours.notes
                }
                for f in facilities
            ]
        
        if query_aspect in ["location", "all"]:
            result["locations"] = [
                {"name": f.name, "location": f.location}
                for f in facilities
            ]
        
        if query_aspect in ["amenities", "all"]:
            result["amenities"] = [
                {
                    "name": f.name,
                    "features": f.amenities
                }
                for f in facilities
            ]
        
        if query_aspect in ["booking", "all"]:
            result["booking_info"] = [
                {
                    "name": f.name,
                    "reservation_required": f.reservation_required,
                    "contact": f.contact
                }
                for f in facilities
            ]
        
        await params.result_callback(result)
        logger.info(f"✓ Provided info for {len(facilities)} facilities")
        
    except Exception as e:
        logger.error(f"Error in get_facility_information: {e}")
        await params.result_callback({
            "success": False,
            "error": str(e)
        })


# ===================================================================
# REGISTRATION
# ===================================================================

def register_hotel_functions(llm_service):
    """
    Register all hotel function handlers with the LLM service.
    
    Args:
        llm_service: The LLM service instance (OpenAI, Azure, etc.)
    """
    logger.info("Registering hotel function handlers...")
    
    llm_service.register_function(
        "get_hotel_information",
        handle_get_hotel_information,
        cancel_on_interruption=False
    )
    
    llm_service.register_function(
        "get_checkin_checkout_info",
        handle_get_checkin_checkout_info,
        cancel_on_interruption=False
    )
    
    llm_service.register_function(
        "get_room_information",
        handle_get_room_information,
        cancel_on_interruption=False
    )
    
    llm_service.register_function(
        "get_facility_information",
        handle_get_facility_information,
        cancel_on_interruption=False
    )
    
    logger.info("✓ Hotel functions registered")
