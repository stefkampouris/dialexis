"""
Pydantic data models for Hotel AI Receptionist system.

This module defines all data structures for hotel information including:
- Hotel core information
- Room types and amenities
- Facilities and services
- Policies and operating hours
"""

from datetime import datetime, time
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


# ===================================================================
# BASIC TYPES & ENUMS
# ===================================================================

class RoomCategory(str, Enum):
    """Room category classifications"""
    STANDARD = "standard"
    DELUXE = "deluxe"
    SUITE = "suite"
    FAMILY = "family"
    ACCESSIBLE = "accessible"


class BedType(str, Enum):
    """Bed type options"""
    KING = "king"
    QUEEN = "queen"
    TWIN = "twin"
    DOUBLE = "double"
    SOFA_BED = "sofa_bed"


class ViewType(str, Enum):
    """View type options"""
    OCEAN = "ocean"
    CITY = "city"
    GARDEN = "garden"
    POOL = "pool"
    MOUNTAIN = "mountain"
    COURTYARD = "courtyard"


class FacilityCategory(str, Enum):
    """Facility categories"""
    DINING = "dining"
    RECREATION = "recreation"
    WELLNESS = "wellness"
    BUSINESS = "business"
    SERVICES = "services"


# ===================================================================
# CORE MODELS
# ===================================================================

class GeoLocation(BaseModel):
    """Geographic coordinates"""
    latitude: float
    longitude: float


class AddressInfo(BaseModel):
    """Hotel address details"""
    street: str
    city: str
    region: str
    country: str
    postal_code: str
    coordinates: Optional[GeoLocation] = None
    directions: str = ""


class ContactInfo(BaseModel):
    """Contact information"""
    phone_main: str
    phone_reservations: Optional[str] = None
    phone_concierge: Optional[str] = None
    email_main: str
    email_reservations: Optional[str] = None
    website: Optional[str] = None


class TimeRange(BaseModel):
    """Time range for operating hours"""
    open: str  # Format: "HH:MM"
    close: str  # Format: "HH:MM"
    
    def __str__(self) -> str:
        return f"{self.open} - {self.close}"


class OperatingHours(BaseModel):
    """Operating hours with day-specific times"""
    monday: Optional[TimeRange] = None
    tuesday: Optional[TimeRange] = None
    wednesday: Optional[TimeRange] = None
    thursday: Optional[TimeRange] = None
    friday: Optional[TimeRange] = None
    saturday: Optional[TimeRange] = None
    sunday: Optional[TimeRange] = None
    seasonal: Optional[str] = None
    notes: str = ""
    
    def get_day_hours(self, day_name: str) -> Optional[TimeRange]:
        """Get hours for a specific day"""
        return getattr(self, day_name.lower(), None)
    
    def is_open_24_7(self) -> bool:
        """Check if facility is open 24/7"""
        all_days = [self.monday, self.tuesday, self.wednesday, 
                   self.thursday, self.friday, self.saturday, self.sunday]
        return all(
            day and day.open == "00:00" and day.close == "23:59" 
            for day in all_days
        )


class FeeStructure(BaseModel):
    """Fee/pricing structure"""
    amount: float
    currency: str = "USD"
    unit: str = "per_item"  # per_item, per_hour, per_day, per_person
    description: str = ""


class CheckInPolicy(BaseModel):
    """Check-in policy details"""
    standard_time: str  # Format: "HH:MM"
    early_checkin_available: bool = False
    early_checkin_fee: Optional[float] = None
    early_checkin_guaranteed_time: Optional[str] = None
    early_checkin_description: str = ""
    requirements: List[str] = Field(default_factory=list)
    deposit_required: bool = False
    deposit_amount: Optional[float] = None
    deposit_description: str = ""


class CheckOutPolicy(BaseModel):
    """Check-out policy details"""
    standard_time: str  # Format: "HH:MM"
    late_checkout_available: bool = False
    late_checkout_fee: Optional[float] = None
    late_checkout_latest_time: Optional[str] = None
    late_checkout_description: str = ""
    express_checkout_available: bool = False
    express_checkout_description: str = ""


class HotelPolicies(BaseModel):
    """All hotel policies"""
    check_in: CheckInPolicy
    check_out: CheckOutPolicy
    cancellation_policy: str = ""
    pet_policy: str = ""
    smoking_policy: str = ""
    age_requirement: int = 18


# ===================================================================
# HOTEL INFORMATION
# ===================================================================

class HotelInfo(BaseModel):
    """Core hotel information"""
    hotel_id: str
    name: str
    brand: str = ""
    star_rating: int = Field(ge=1, le=5)
    address: AddressInfo
    contact: ContactInfo
    description: str
    tagline: str = ""
    awards: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    policies: Optional[HotelPolicies] = None
    
    def get_full_address(self) -> str:
        """Get formatted full address"""
        return f"{self.address.street}, {self.address.city}, {self.address.region} {self.address.postal_code}, {self.address.country}"


# ===================================================================
# ROOM MODELS
# ===================================================================

class BedConfig(BaseModel):
    """Bed configuration options"""
    bed_type: str  # Use BedType enum values
    quantity: int = 1


class WifiInfo(BaseModel):
    """WiFi amenity details"""
    available: bool = True
    speed: str = "High-speed"
    cost: str = "Complimentary"


class TVInfo(BaseModel):
    """TV amenity details"""
    available: bool = True
    size_inches: Optional[int] = None
    type: str = "Smart TV"
    channels: str = "Cable"


class BathroomAmenities(BaseModel):
    """Bathroom amenities"""
    type: str = "Full bathroom"  # Full bathroom, Shower only, etc.
    features: List[str] = Field(default_factory=list)
    # Examples: "Rain shower", "Bathtub", "Luxury toiletries", "Hairdryer", "Bathrobes"


class RoomAmenities(BaseModel):
    """In-room amenities"""
    wifi: WifiInfo = Field(default_factory=WifiInfo)
    tv: TVInfo = Field(default_factory=TVInfo)
    climate_control: bool = True
    minibar: bool = False
    minibar_pricing: Optional[str] = None
    coffee_tea: bool = False
    coffee_tea_type: Optional[str] = None
    safe: bool = True
    safe_description: Optional[str] = None
    workspace: bool = False
    workspace_description: Optional[str] = None
    balcony: bool = False
    balcony_features: Optional[str] = None
    bathroom: BathroomAmenities = Field(default_factory=BathroomAmenities)
    smoking_allowed: bool = False
    other_amenities: List[str] = Field(default_factory=list)


class RoomType(BaseModel):
    """Room type definition"""
    room_type_id: str
    name: str
    category: str  # Use RoomCategory enum values
    description: str
    size_sqm: float
    max_occupancy: int
    bed_configuration: List[BedConfig]
    view_types: List[str] = Field(default_factory=list)  # Use ViewType enum values
    floor_range: str = ""
    amenities: RoomAmenities
    base_rate: Optional[float] = None
    images: List[str] = Field(default_factory=list)
    
    def get_bed_description(self) -> str:
        """Get human-readable bed description"""
        descriptions = []
        for bed in self.bed_configuration:
            qty = bed.quantity
            bed_name = bed.bed_type.replace("_", " ").title()
            if qty == 1:
                descriptions.append(f"1 {bed_name}")
            else:
                descriptions.append(f"{qty} {bed_name}s")
        return " and ".join(descriptions)


# ===================================================================
# FACILITY MODELS
# ===================================================================

class Facility(BaseModel):
    """Hotel facility definition"""
    facility_id: str
    name: str
    category: str  # Use FacilityCategory enum values
    subcategory: str
    description: str
    operating_hours: OperatingHours
    location: str
    capacity: Optional[int] = None
    reservation_required: bool = False
    fees: Optional[FeeStructure] = None
    contact: Optional[str] = None
    amenities: Dict[str, Any] = Field(default_factory=dict)
    
    def is_currently_open(self, current_time: datetime) -> bool:
        """Check if facility is currently open"""
        day_name = current_time.strftime("%A").lower()
        day_hours = self.operating_hours.get_day_hours(day_name)
        
        if not day_hours:
            return False
        
        current_time_str = current_time.strftime("%H:%M")
        return day_hours.open <= current_time_str <= day_hours.close


class DiningFacility(Facility):
    """Restaurant, bar, or dining facility"""
    cuisine_type: Optional[str] = None
    dress_code: Optional[str] = None
    menu_highlights: List[str] = Field(default_factory=list)
    dietary_options: List[str] = Field(default_factory=list)
    chef_info: Optional[str] = None
    breakfast_included: bool = False
    breakfast_type: Optional[str] = None
    breakfast_price: Optional[float] = None
    room_service: bool = False
    room_service_hours: Optional[OperatingHours] = None


class PoolFacility(Facility):
    """Pool facility"""
    pool_type: str = "standard"  # infinity_edge, olympic, lap, etc.
    heated: bool = False
    depth: Optional[str] = None
    poolside_bar: bool = False
    cabanas_available: bool = False
    cabana_rate: Optional[float] = None
    towel_service: bool = True
    lifeguard: bool = False


class GymFacility(Facility):
    """Fitness center/gym"""
    equipment: List[str] = Field(default_factory=list)
    personal_training: bool = False
    classes: List[str] = Field(default_factory=list)
    lockers: bool = True
    towels: bool = True


class SpaFacility(Facility):
    """Spa and wellness facility"""
    treatments: List[Dict[str, Any]] = Field(default_factory=list)
    couples_treatments: bool = False
    facilities: List[str] = Field(default_factory=list)  # Sauna, steam room, etc.
    products: Optional[str] = None


# ===================================================================
# HELPER FUNCTIONS
# ===================================================================

def validate_time_format(time_str: str) -> bool:
    """Validate time string is in HH:MM format"""
    try:
        hour, minute = time_str.split(":")
        return 0 <= int(hour) <= 23 and 0 <= int(minute) <= 59
    except:
        return False
