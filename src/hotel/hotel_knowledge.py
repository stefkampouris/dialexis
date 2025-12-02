"""
Hotel Knowledge Base - Centralized repository for hotel information.

This module provides access to all static hotel data including:
- Hotel information and policies
- Room types and configurations  
- Facilities and their operating hours
- Services and amenities

Data is loaded from YAML configuration files and cached for performance.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from functools import lru_cache
from loguru import logger

from src.hotel.models import (
    HotelInfo,
    AddressInfo,
    ContactInfo,
    RoomType,
    RoomAmenities,
    BedConfig,
    Facility,
    DiningFacility,
    PoolFacility,
    GymFacility,
    SpaFacility,
    OperatingHours,
    TimeRange,
    HotelPolicies,
    CheckInPolicy,
    CheckOutPolicy,
    WifiInfo,
    TVInfo,
    BathroomAmenities,
    FeeStructure,
    GeoLocation,
)


class HotelKnowledgeBase:
    """
    Centralized knowledge repository for hotel information.
    
    Loads hotel data from YAML configuration and provides methods
    to query and retrieve information in a structured way.
    """
    
    def __init__(self, config_path: str = "data/hotel_config.yaml"):
        """
        Initialize knowledge base with hotel configuration.
        
        Args:
            config_path: Path to hotel configuration YAML file
        """
        self.config_path = Path(config_path)
        self._hotel_info: Optional[HotelInfo] = None
        self._rooms: Dict[str, RoomType] = {}
        self._facilities: Dict[str, Facility] = {}
        self._config_data: Dict[str, Any] = {}
        
        # Load configuration on initialization
        self._load_configuration()
    
    def _load_configuration(self) -> None:
        """Load hotel configuration from YAML file"""
        try:
            if not self.config_path.exists():
                logger.warning(f"Hotel config file not found: {self.config_path}")
                logger.warning("Using default/empty configuration")
                return
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config_data = yaml.safe_load(f)
            
            logger.info(f"✓ Loaded hotel configuration from {self.config_path}")
            
            # Parse configuration into models
            self._parse_hotel_info()
            self._parse_rooms()
            self._parse_facilities()
            
        except Exception as e:
            logger.error(f"Error loading hotel configuration: {e}")
            raise
    
    def _parse_hotel_info(self) -> None:
        """Parse hotel information from config"""
        if 'hotel' not in self._config_data:
            return
        
        hotel_data = self._config_data['hotel']
        policies_data = self._config_data.get('policies', {})
        
        # Parse address
        address = AddressInfo(
            **hotel_data.get('address', {})
        )
        
        # Parse contact
        contact = ContactInfo(
            **hotel_data.get('contact', {})
        )
        
        # Parse policies
        check_in_policy = CheckInPolicy(
            **policies_data.get('check_in', {})
        )
        check_out_policy = CheckOutPolicy(
            **policies_data.get('check_out', {})
        )
        policies = HotelPolicies(
            check_in=check_in_policy,
            check_out=check_out_policy,
            **{k: v for k, v in policies_data.items() 
               if k not in ['check_in', 'check_out']}
        )
        
        # Create hotel info model
        self._hotel_info = HotelInfo(
            hotel_id=hotel_data.get('id'),
            name=hotel_data.get('name'),
            brand=hotel_data.get('brand', ''),
            star_rating=hotel_data.get('star_rating'),
            address=address,
            contact=contact,
            description=hotel_data.get('description', ''),
            tagline=hotel_data.get('tagline', ''),
            awards=hotel_data.get('awards', []),
            certifications=hotel_data.get('certifications', []),
            policies=policies
        )
        
        logger.info(f"✓ Parsed hotel info: {self._hotel_info.name}")
    
    def _parse_rooms(self) -> None:
        """Parse room types from config"""
        if 'rooms' not in self._config_data:
            return
        
        for room_data in self._config_data['rooms']:
            try:
                # Parse bed configuration
                bed_config = [
                    BedConfig(**bed) for bed in room_data.get('bed_configuration', [])
                ]
                
                # Parse amenities
                amenities_data = room_data.get('amenities', {})
                
                # Parse WiFi
                wifi = WifiInfo(**amenities_data.get('wifi', {}))
                
                # Parse TV
                tv = TVInfo(**amenities_data.get('tv', {}))
                
                # Parse bathroom
                bathroom = BathroomAmenities(**amenities_data.get('bathroom', {}))
                
                # Create amenities
                amenities = RoomAmenities(
                    wifi=wifi,
                    tv=tv,
                    bathroom=bathroom,
                    climate_control=amenities_data.get('climate_control', True),
                    minibar=amenities_data.get('minibar', {}).get('available', False),
                    minibar_pricing=amenities_data.get('minibar', {}).get('pricing'),
                    coffee_tea=amenities_data.get('coffee_tea', {}).get('available', False),
                    coffee_tea_type=amenities_data.get('coffee_tea', {}).get('type'),
                    safe=amenities_data.get('safe', {}).get('available', True),
                    safe_description=amenities_data.get('safe', {}).get('description'),
                    workspace=amenities_data.get('workspace', {}).get('available', False),
                    workspace_description=amenities_data.get('workspace', {}).get('description'),
                    balcony=amenities_data.get('balcony', False),
                    balcony_features=amenities_data.get('balcony_features'),
                    smoking_allowed=amenities_data.get('smoking_allowed', False),
                )
                
                # Create room type
                room = RoomType(
                    room_type_id=room_data['id'],
                    name=room_data['name'],
                    category=room_data['category'],
                    description=room_data.get('description', ''),
                    size_sqm=room_data.get('size_sqm', 0),
                    max_occupancy=room_data.get('max_occupancy', 2),
                    bed_configuration=bed_config,
                    view_types=room_data.get('view_types', []),
                    floor_range=room_data.get('floor_range', ''),
                    amenities=amenities,
                    base_rate=room_data.get('base_rate'),
                    images=room_data.get('images', [])
                )
                
                self._rooms[room.room_type_id] = room
                logger.debug(f"Parsed room type: {room.name}")
                
            except Exception as e:
                logger.error(f"Error parsing room {room_data.get('name', 'unknown')}: {e}")
        
        logger.info(f"✓ Parsed {len(self._rooms)} room types")
    
    def _parse_facilities(self) -> None:
        """Parse facilities from config"""
        if 'facilities' not in self._config_data:
            return
        
        for fac_data in self._config_data['facilities']:
            try:
                # Parse operating hours
                hours_data = fac_data.get('operating_hours', {})
                operating_hours = OperatingHours(
                    monday=TimeRange(**hours_data['monday']) if 'monday' in hours_data and hours_data['monday'] else None,
                    tuesday=TimeRange(**hours_data['tuesday']) if 'tuesday' in hours_data and hours_data['tuesday'] else None,
                    wednesday=TimeRange(**hours_data['wednesday']) if 'wednesday' in hours_data and hours_data['wednesday'] else None,
                    thursday=TimeRange(**hours_data['thursday']) if 'thursday' in hours_data and hours_data['thursday'] else None,
                    friday=TimeRange(**hours_data['friday']) if 'friday' in hours_data and hours_data['friday'] else None,
                    saturday=TimeRange(**hours_data['saturday']) if 'saturday' in hours_data and hours_data['saturday'] else None,
                    sunday=TimeRange(**hours_data['sunday']) if 'sunday' in hours_data and hours_data['sunday'] else None,
                    seasonal=hours_data.get('seasonal'),
                    notes=hours_data.get('notes', '')
                )
                
                # Determine facility type and create appropriate model
                category = fac_data.get('category')
                subcategory = fac_data.get('subcategory')
                details = fac_data.get('details', {})
                
                # Base facility data
                base_data = {
                    'facility_id': fac_data['id'],
                    'name': fac_data['name'],
                    'category': category,
                    'subcategory': subcategory,
                    'description': fac_data.get('description', ''),
                    'operating_hours': operating_hours,
                    'location': fac_data.get('location', ''),
                    'capacity': fac_data.get('capacity'),
                    'reservation_required': fac_data.get('reservation_required', False),
                    'contact': fac_data.get('contact'),
                    'amenities': details
                }
                
                # Create specialized facility types
                if subcategory == 'restaurant' or subcategory == 'bar':
                    facility = DiningFacility(
                        **base_data,
                        cuisine_type=details.get('cuisine_type'),
                        dress_code=details.get('dress_code'),
                        menu_highlights=details.get('menu_highlights', []),
                        dietary_options=details.get('dietary_options', []),
                        chef_info=details.get('chef_info'),
                        breakfast_included=details.get('breakfast', {}).get('included', False),
                        breakfast_type=details.get('breakfast', {}).get('type'),
                        breakfast_price=details.get('breakfast', {}).get('price'),
                        room_service=details.get('room_service', False)
                    )
                elif subcategory == 'pool':
                    facility = PoolFacility(
                        **base_data,
                        pool_type=details.get('pool_type', 'standard'),
                        heated=details.get('heated', False),
                        depth=details.get('depth'),
                        poolside_bar=details.get('poolside_bar', False),
                        cabanas_available=details.get('cabanas', {}).get('available', False),
                        cabana_rate=details.get('cabanas', {}).get('daily_rate'),
                        towel_service=details.get('towel_service', True),
                        lifeguard=details.get('lifeguard', False)
                    )
                elif subcategory == 'gym':
                    facility = GymFacility(
                        **base_data,
                        equipment=details.get('equipment', []),
                        personal_training=details.get('personal_training', {}).get('available', False),
                        classes=details.get('classes', []),
                        lockers=details.get('lockers', True),
                        towels=details.get('towels', True)
                    )
                elif subcategory == 'spa':
                    facility = SpaFacility(
                        **base_data,
                        treatments=details.get('treatments', []),
                        couples_treatments=details.get('couples_treatments', False),
                        facilities=details.get('facilities', []),
                        products=details.get('products')
                    )
                else:
                    # Generic facility
                    facility = Facility(**base_data)
                
                self._facilities[facility.facility_id] = facility
                logger.debug(f"Parsed facility: {facility.name}")
                
            except Exception as e:
                logger.error(f"Error parsing facility {fac_data.get('name', 'unknown')}: {e}")
        
        logger.info(f"✓ Parsed {len(self._facilities)} facilities")
    
    # ===================================================================
    # PUBLIC ACCESS METHODS
    # ===================================================================
    
    def get_hotel_info(self) -> Optional[HotelInfo]:
        """Get core hotel information"""
        return self._hotel_info
    
    def get_checkin_info(self) -> Dict[str, Any]:
        """Get check-in related information"""
        if not self._hotel_info or not self._hotel_info.policies:
            return {}
        
        policy = self._hotel_info.policies.check_in
        return {
            "time": policy.standard_time,
            "early_available": policy.early_checkin_available,
            "early_fee": policy.early_checkin_fee,
            "early_guaranteed_time": policy.early_checkin_guaranteed_time,
            "requirements": policy.requirements,
            "deposit_required": policy.deposit_required,
            "deposit_amount": policy.deposit_amount,
        }
    
    def get_checkout_info(self) -> Dict[str, Any]:
        """Get check-out related information"""
        if not self._hotel_info or not self._hotel_info.policies:
            return {}
        
        policy = self._hotel_info.policies.check_out
        return {
            "time": policy.standard_time,
            "late_available": policy.late_checkout_available,
            "late_fee": policy.late_checkout_fee,
            "late_latest_time": policy.late_checkout_latest_time,
            "express_available": policy.express_checkout_available,
        }
    
    def get_room_types(self, filters: Optional[Dict] = None) -> List[RoomType]:
        """
        Get room types, optionally filtered.
        
        Args:
            filters: Optional filters (category, min_occupancy, view_type, etc.)
        
        Returns:
            List of matching room types
        """
        rooms = list(self._rooms.values())
        
        if not filters:
            return rooms
        
        # Apply filters
        if 'category' in filters and filters['category']:
            rooms = [r for r in rooms if r.category == filters['category']]
        
        if 'min_occupancy' in filters:
            rooms = [r for r in rooms if r.max_occupancy >= filters['min_occupancy']]
        
        if 'view_type' in filters:
            rooms = [r for r in rooms if filters['view_type'] in r.view_types]
        
        if 'accessible' in filters and filters['accessible']:
            rooms = [r for r in rooms if r.category == 'accessible']
        
        return rooms
    
    def get_room_by_id(self, room_id: str) -> Optional[RoomType]:
        """Get specific room type by ID"""
        return self._rooms.get(room_id)
    
    def compare_rooms(self, room_type_ids: List[str]) -> Dict[str, Any]:
        """
        Compare multiple room types.
        
        Args:
            room_type_ids: List of room IDs to compare
        
        Returns:
            Comparison data structure
        """
        rooms = [self._rooms.get(rid) for rid in room_type_ids]
        rooms = [r for r in rooms if r is not None]
        
        if not rooms:
            return {"error": "No valid rooms found"}
        
        comparison = {
            "rooms": [],
            "differences": {
                "size": {},
                "occupancy": {},
                "beds": {},
                "views": {},
                "rate": {}
            }
        }
        
        for room in rooms:
            comparison["rooms"].append({
                "id": room.room_type_id,
                "name": room.name,
                "category": room.category,
                "size_sqm": room.size_sqm,
                "max_occupancy": room.max_occupancy,
                "beds": room.get_bed_description(),
                "views": room.view_types,
                "base_rate": room.base_rate
            })
            
            comparison["differences"]["size"][room.name] = room.size_sqm
            comparison["differences"]["occupancy"][room.name] = room.max_occupancy
            comparison["differences"]["beds"][room.name] = room.get_bed_description()
            comparison["differences"]["views"][room.name] = room.view_types
            comparison["differences"]["rate"][room.name] = room.base_rate
        
        return comparison
    
    def get_facility_by_id(self, facility_id: str) -> Optional[Facility]:
        """Get specific facility by ID"""
        return self._facilities.get(facility_id)
    
    def get_facilities_by_category(self, category: str) -> List[Facility]:
        """Get all facilities in a category"""
        return [f for f in self._facilities.values() if f.category == category]
    
    def get_all_facilities(self) -> List[Facility]:
        """Get all facilities"""
        return list(self._facilities.values())
    
    def search_facilities(self, query: str) -> List[Facility]:
        """
        Search facilities by name or description.
        
        Args:
            query: Search query string
        
        Returns:
            List of matching facilities
        """
        query_lower = query.lower()
        return [
            f for f in self._facilities.values()
            if query_lower in f.name.lower() or query_lower in f.description.lower()
        ]
    
    def reload_configuration(self) -> None:
        """Reload configuration from file (useful for updates)"""
        logger.info("Reloading hotel configuration...")
        self._hotel_info = None
        self._rooms.clear()
        self._facilities.clear()
        self._load_configuration()


# Global knowledge base instance (initialized on import)
knowledge_base: Optional[HotelKnowledgeBase] = None


def initialize_knowledge_base(config_path: str = "data/hotel_config.yaml") -> HotelKnowledgeBase:
    """
    Initialize the global knowledge base.
    
    Args:
        config_path: Path to hotel configuration file
    
    Returns:
        Initialized knowledge base instance
    """
    global knowledge_base
    knowledge_base = HotelKnowledgeBase(config_path)
    return knowledge_base


def get_knowledge_base() -> Optional[HotelKnowledgeBase]:
    """Get the global knowledge base instance"""
    return knowledge_base
