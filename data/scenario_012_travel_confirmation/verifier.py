"""
Verifier for scenario scenario_012_travel_confirmation
Generated on 2026-02-05T22:39:57.294754
"""


from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Tuple

from gordon import TaskVerifier

def validation_function(state: Dict[str, Any]) -> Tuple[float, List[TaskVerifier]]:
    """
    Validate that calendar events were created for flight confirmations.
    
    Checks that:
    1. Appropriate travel time blocks exist on the calendar covering the full flight duration
    2. Flight numbers appear in the event title or description
    """
    # Hardcoded expected flight times and numbers
    outbound_departure = "2026-01-26T14:15:00.000Z"
    outbound_arrival = "2026-01-26T16:15:00.000Z"
    outbound_flight_number = "UA7070"
    
    return_departure = "2026-01-30T02:30:00.000Z"
    return_arrival = "2026-01-30T04:30:00.000Z"
    return_flight_number = "UA3685"
    
    events = state.get("calendar-clone").get("events", [])
    checks: List[TaskVerifier] = []
    
    # Parse datetime objects for comparison
    outbound_dep_dt = datetime.fromisoformat(outbound_departure.replace('Z', '+00:00'))
    outbound_arr_dt = datetime.fromisoformat(outbound_arrival.replace('Z', '+00:00'))
    return_dep_dt = datetime.fromisoformat(return_departure.replace('Z', '+00:00'))
    return_arr_dt = datetime.fromisoformat(return_arrival.replace('Z', '+00:00'))
    
    # Allow 30 minutes buffer before departure for airport arrival
    buffer_time = timedelta(minutes=0)
    
    # Look for travel blocks on calendar
    outbound_event_found = None
    return_event_found = None
    
    for event in events:
        event_title = event.get("title", "")
        event_description = event.get("description", "")
        event_title_lower = event_title.lower() if event_title else ""
        event_description_lower = event_description.lower() if event_description else ""
        
        # Parse event times
        try:
            event_start = datetime.fromisoformat(event["start"].replace('Z', '+00:00'))
            event_end = datetime.fromisoformat(event["end"].replace('Z', '+00:00'))
        except:
            continue
        
        # Check for outbound flight
        if not outbound_event_found:
            # Check if event properly blocks the outbound flight time
            # Event should start at or before departure (with buffer) and end at or after arrival
            if (event_start <= outbound_dep_dt - buffer_time and 
                event_end >= outbound_arr_dt):
                # Also check for flight number in title or description
                if (outbound_flight_number.lower() in event_title_lower or 
                    outbound_flight_number.lower() in event_description_lower):
                    outbound_event_found = event
        
        # Check for return flight
        if not return_event_found:
            # Check if event properly blocks the return flight time
            if (event_start <= return_dep_dt - buffer_time and 
                event_end >= return_arr_dt):
                # Also check for flight number in title or description
                if (return_flight_number.lower() in event_title_lower or 
                    return_flight_number.lower() in event_description_lower):
                    return_event_found = event
    
    # Check 1: Outbound flight calendar event
    checks.append(TaskVerifier(
        name="outbound_flight_check",
        verdict=bool(outbound_event_found),
        reason=f"Calendar event found for outbound flight {outbound_flight_number}" if outbound_event_found else
               f"No calendar event found that blocks time for outbound flight {outbound_flight_number}"
    ))
    
    # Check 2: Return flight calendar event
    checks.append(TaskVerifier(
        name="return_flight_check",
        verdict=bool(return_event_found),
        reason=f"Calendar event found for return flight {return_flight_number}" if return_event_found else
               f"No calendar event found that blocks time for return flight {return_flight_number}"
    ))
    
    # Calculate reward: each check is worth 1/2
    passed_checks = sum(1 for c in checks if c.verdict)
    reward = passed_checks / len(checks) if checks else 0.0
    
    return reward, checks


# The validation function is available as 'validation_function'
