"""
Google Calendar Integration for Dental Clinic

Provides functions to check doctor availability and manage appointments
using the Google Calendar API.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleCalendarService:
    """Service for interacting with Google Calendar API."""
    
    # Scopes required for calendar operations
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',  # Full calendar access for create/update/delete
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    def __init__(self):
        """Initialize the Google Calendar service."""
        self.service = None
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the Google Calendar API service with credentials."""
        try:
            # Path to service account credentials JSON file
            credentials_path = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_PATH")
            
            if not credentials_path:
                logger.warning("GOOGLE_CALENDAR_CREDENTIALS_PATH not set. Calendar functions will not work.")
                return
            
            # Use service account credentials
            creds = ServiceAccountCredentials.from_service_account_file(
                credentials_path,
                scopes=self.SCOPES
            )
            
            # Build the Calendar service
            self.service = build('calendar', 'v3', credentials=creds)
            logger.info("✓ Google Calendar service initialized")
            
        except Exception as e:
            logger.error(f"✗ Failed to initialize Google Calendar service: {e}")
            self.service = None
    
    def get_availability(
        self,
        start_date: str,
        end_date: Optional[str] = None,
        timezone: str = "Europe/Athens"
    ) -> Dict:
        """
        Get free/busy information for the calendar.
        
        Args:
            start_date: Start date/time in ISO format (e.g., "2025-11-16T09:00:00")
            end_date: End date/time in ISO format. If None, defaults to start_date + 7 days
            timezone: Timezone for the query (default: Europe/Athens for Greece)
        
        Returns:
            Dict containing:
                - free_slots: List of available time slots
                - busy_slots: List of busy time slots
                - timezone: Timezone used
        """
        if not self.service:
            return {
                "error": "Calendar service not initialized",
                "free_slots": [],
                "busy_slots": []
            }
        
        try:
            # Parse start date
            start_dt = datetime.fromisoformat(start_date)
            
            # If no end date, default to 7 days from start
            if not end_date:
                end_dt = start_dt + timedelta(days=7)
                end_date = end_dt.isoformat()
            
            # Format for API (RFC3339)
            time_min = start_dt.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
            time_max = datetime.fromisoformat(end_date).strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
            
            # Query free/busy information
            body = {
                "timeMin": time_min,
                "timeMax": time_max,
                "timeZone": timezone,
                "items": [{"id": self.calendar_id}]
            }
            
            logger.info(f"Querying calendar availability from {start_date} to {end_date}")
            
            freebusy_result = self.service.freebusy().query(body=body).execute()
            
            # Extract busy periods
            calendar_info = freebusy_result.get('calendars', {}).get(self.calendar_id, {})
            busy_slots = calendar_info.get('busy', [])
            
            # Calculate free slots (simple logic: working hours 9 AM - 6 PM, Monday-Friday)
            free_slots = self._calculate_free_slots(
                start_dt,
                datetime.fromisoformat(end_date),
                busy_slots,
                timezone
            )
            
            return {
                "success": True,
                "free_slots": free_slots,
                "busy_slots": busy_slots,
                "timezone": timezone,
                "calendar_id": self.calendar_id
            }
            
        except HttpError as error:
            logger.error(f"Google Calendar API error: {error}")
            return {
                "error": f"Calendar API error: {str(error)}",
                "free_slots": [],
                "busy_slots": []
            }
        except Exception as e:
            logger.error(f"Error getting calendar availability: {e}")
            return {
                "error": str(e),
                "free_slots": [],
                "busy_slots": []
            }
    
    def _calculate_free_slots(
        self,
        start_dt: datetime,
        end_dt: datetime,
        busy_slots: List[Dict],
        timezone: str,
        slot_duration_minutes: int = 30
    ) -> List[Dict]:
        """
        Calculate available time slots based on busy periods.
        
        Args:
            start_dt: Start datetime
            end_dt: End datetime
            busy_slots: List of busy time periods from Google Calendar
            timezone: Timezone
            slot_duration_minutes: Duration of each appointment slot (default: 30 min)
        
        Returns:
            List of free time slots with start and end times
        """
        free_slots = []
        
        # Define working hours (9 AM - 6 PM)
        WORK_START = 9
        WORK_END = 18
        
        # Iterate through each day in the range
        current_day = start_dt.date()
        end_day = end_dt.date()
        
        while current_day <= end_day:
            # Skip weekends
            if current_day.weekday() >= 5:  # Saturday = 5, Sunday = 6
                current_day += timedelta(days=1)
                continue
            
            # Create time slots for this day
            day_start = datetime.combine(current_day, datetime.min.time()).replace(hour=WORK_START)
            day_end = datetime.combine(current_day, datetime.min.time()).replace(hour=WORK_END)
            
            # Generate slots for the day
            current_slot_start = day_start
            
            while current_slot_start + timedelta(minutes=slot_duration_minutes) <= day_end:
                current_slot_end = current_slot_start + timedelta(minutes=slot_duration_minutes)
                
                # Check if this slot overlaps with any busy period
                is_free = True
                for busy in busy_slots:
                    busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                    busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                    
                    # Remove timezone info for comparison
                    busy_start = busy_start.replace(tzinfo=None)
                    busy_end = busy_end.replace(tzinfo=None)
                    
                    # Check for overlap
                    if (current_slot_start < busy_end and current_slot_end > busy_start):
                        is_free = False
                        break
                
                if is_free:
                    free_slots.append({
                        "start": current_slot_start.isoformat(),
                        "end": current_slot_end.isoformat(),
                        "duration_minutes": slot_duration_minutes
                    })
                
                current_slot_start = current_slot_end
            
            current_day += timedelta(days=1)
        
        return free_slots
    
    def get_upcoming_appointments(
        self,
        days_ahead: int = 7,
        timezone: str = "Europe/Athens"
    ) -> List[Dict]:
        """
        Get list of upcoming appointments.
        
        Args:
            days_ahead: Number of days to look ahead (default: 7)
            timezone: Timezone (default: Europe/Athens)
        
        Returns:
            List of upcoming events/appointments
        """
        if not self.service:
            return []
        
        try:
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'
            time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=50,
                singleEvents=True,
                orderBy='startTime',
                timeZone=timezone
            ).execute()
            
            events = events_result.get('items', [])
            
            appointments = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                appointments.append({
                    "id": event['id'],
                    "summary": event.get('summary', 'Busy'),
                    "start": start,
                    "end": end,
                    "status": event.get('status', 'confirmed')
                })
            
            return appointments
            
        except Exception as e:
            logger.error(f"Error getting upcoming appointments: {e}")
            return []
    
    def create_event(
        self,
        summary: str,
        start_datetime: str,
        end_datetime: str,
        description: Optional[str] = None,
        patient_name: Optional[str] = None,
        patient_phone: Optional[str] = None,
        timezone: str = "Europe/Athens"
    ) -> Dict:
        """
        Create a new appointment in the calendar.
        
        Args:
            summary: Title of the appointment (e.g., "Dental Cleaning")
            start_datetime: Start time in ISO format (e.g., "2025-11-17T09:00:00")
            end_datetime: End time in ISO format
            description: Optional description
            patient_name: Optional patient name
            patient_phone: Optional patient phone number
            timezone: Timezone (default: Europe/Athens)
        
        Returns:
            Dict with success status and event details or error
        """
        if not self.service:
            return {"error": "Calendar service not initialized"}
        
        try:
            # Build event description
            event_description = description or ""
            if patient_name:
                event_description += f"\nΌνομα: {patient_name}"
            if patient_phone:
                event_description += f"\nΤηλέφωνο: {patient_phone}"
            
            # Create event body
            event = {
                'summary': summary,
                'description': event_description.strip(),
                'start': {
                    'dateTime': start_datetime,
                    'timeZone': timezone,
                },
                'end': {
                    'dateTime': end_datetime,
                    'timeZone': timezone,
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 60},  # 1 hour before
                    ],
                },
            }
            
            logger.info(f"📝 Creating event: {summary} at {start_datetime}")
            
            # Insert the event
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            logger.info(f"✓ Event created: {created_event.get('id')}")
            
            return {
                "success": True,
                "event_id": created_event.get('id'),
                "summary": created_event.get('summary'),
                "start": created_event['start'].get('dateTime'),
                "end": created_event['end'].get('dateTime'),
                "htmlLink": created_event.get('htmlLink')
            }
            
        except HttpError as error:
            logger.error(f"Google Calendar API error creating event: {error}")
            return {"error": f"Calendar API error: {str(error)}"}
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            return {"error": str(e)}
    
    def update_event(
        self,
        event_id: str,
        summary: Optional[str] = None,
        start_datetime: Optional[str] = None,
        end_datetime: Optional[str] = None,
        description: Optional[str] = None,
        timezone: str = "Europe/Athens"
    ) -> Dict:
        """
        Update an existing appointment.
        
        Args:
            event_id: The ID of the event to update
            summary: New title (optional)
            start_datetime: New start time in ISO format (optional)
            end_datetime: New end time in ISO format (optional)
            description: New description (optional)
            timezone: Timezone (default: Europe/Athens)
        
        Returns:
            Dict with success status and updated event details or error
        """
        if not self.service:
            return {"error": "Calendar service not initialized"}
        
        try:
            # First, get the existing event
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            # Update fields if provided
            if summary:
                event['summary'] = summary
            if description is not None:
                event['description'] = description
            if start_datetime:
                event['start'] = {
                    'dateTime': start_datetime,
                    'timeZone': timezone,
                }
            if end_datetime:
                event['end'] = {
                    'dateTime': end_datetime,
                    'timeZone': timezone,
                }
            
            logger.info(f"✏️ Updating event: {event_id}")
            
            # Update the event using PATCH for partial updates
            updated_event = self.service.events().patch(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            logger.info(f"✓ Event updated: {event_id}")
            
            return {
                "success": True,
                "event_id": updated_event.get('id'),
                "summary": updated_event.get('summary'),
                "start": updated_event['start'].get('dateTime'),
                "end": updated_event['end'].get('dateTime'),
                "htmlLink": updated_event.get('htmlLink')
            }
            
        except HttpError as error:
            logger.error(f"Google Calendar API error updating event: {error}")
            return {"error": f"Calendar API error: {str(error)}"}
        except Exception as e:
            logger.error(f"Error updating event: {e}")
            return {"error": str(e)}
    
    def delete_event(self, event_id: str) -> Dict:
        """
        Delete/cancel an appointment.
        
        Args:
            event_id: The ID of the event to delete
        
        Returns:
            Dict with success status or error
        """
        if not self.service:
            return {"error": "Calendar service not initialized"}
        
        try:
            logger.info(f"🗑️ Deleting event: {event_id}")
            
            # Delete the event
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            logger.info(f"✓ Event deleted: {event_id}")
            
            return {
                "success": True,
                "event_id": event_id,
                "message": "Event deleted successfully"
            }
            
        except HttpError as error:
            logger.error(f"Google Calendar API error deleting event: {error}")
            return {"error": f"Calendar API error: {str(error)}"}
        except Exception as e:
            logger.error(f"Error deleting event: {e}")
            return {"error": str(e)}


# Global instance
calendar_service = GoogleCalendarService()
