"""
Verifier for scenario scenario_013_cascading_changes
Generated on 2026-02-04T11:25:31.206195
"""


from typing import Dict, Any
from datetime import datetime, timezone

def validation_function(state: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
    """
    Standalone validation function for cascading changes scenario.
    
    Checks if prep and debrief meetings were rescheduled when main meeting moved.
    """
    
    # New expected times (main meeting moved by external partner)
    new_main_start = datetime.fromisoformat("2026-01-26T18:30:00+00:00")
    new_prep_start = datetime.fromisoformat("2026-01-26T18:15:00+00:00")
    new_prep_end = datetime.fromisoformat("2026-01-26T18:30:00+00:00")
    new_debrief_start = datetime.fromisoformat("2026-01-26T19:30:00+00:00")
    new_debrief_end = datetime.fromisoformat("2026-01-26T19:45:00+00:00")
    
    # Original times (should no longer have prep/debrief)
    original_prep_start = datetime.fromisoformat("2026-01-23T17:45:00+00:00")
    original_debrief_start = datetime.fromisoformat("2026-01-23T19:00:00+00:00")
    
    # Ensure all times are timezone-aware
    for dt in [new_main_start, new_prep_start, new_prep_end, new_debrief_start, 
               new_debrief_end, original_prep_start, original_debrief_start]:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    
    meeting_topic = "Partnership Strategy Review"
    external_email = "ethan.park@ridgeviewadvisors.com"
    internal_emails = {'aiden.walker@helixgrid.com', 'mei.tan@helixgrid.com', 'alan@helixgrid.com', 'noah.fitzgerald@helixgrid.com'}
    
    events = state.get("calendar-clone").get("events", [])
    
    # Find meetings
    main_meeting = None
    prep_meeting = None
    debrief_meeting = None
    old_prep_found = False
    old_debrief_found = False
    
    for event in events:
        # Events are always in UTC/Zulu time format
        # Handle both with and without milliseconds
        start_str = event["start"].replace('Z', '+00:00').replace('.000+00:00', '+00:00')
        end_str = event["end"].replace('Z', '+00:00').replace('.000+00:00', '+00:00')
        
        event_start = datetime.fromisoformat(start_str)
        event_end = datetime.fromisoformat(end_str)
        
        # Ensure timezone awareness (should already be UTC)
        if event_start.tzinfo is None:
            event_start = event_start.replace(tzinfo=timezone.utc)
        if event_end.tzinfo is None:
            event_end = event_end.replace(tzinfo=timezone.utc)
        
        event_title = event.get("title", "").lower()
        attendee_emails = {att["email"] for att in event.get("attendees", [])}
        
        # Check for main meeting at new time (organized by external)
        if (abs((event_start - new_main_start).total_seconds()) < 300 and
            meeting_topic.lower() in event_title and
            external_email in attendee_emails):
            # Verify external partner is organizer
            for att in event.get("attendees", []):
                if att["email"] == external_email and att.get("isOrganizer", False):
                    main_meeting = event
                    break
        
        # Check for prep meeting at NEW time (internal only)
        elif (abs((event_start - new_prep_start).total_seconds()) < 300 and
              abs((event_end - new_prep_end).total_seconds()) < 300 and
              "prep" in event_title and
              external_email not in attendee_emails and
              internal_emails.issubset(attendee_emails)):
            prep_meeting = event
        
        # Check for debrief meeting at NEW time (internal only)
        elif (abs((event_start - new_debrief_start).total_seconds()) < 300 and
              abs((event_end - new_debrief_end).total_seconds()) < 300 and
              "debrief" in event_title and
              external_email not in attendee_emails and
              internal_emails.issubset(attendee_emails)):
            debrief_meeting = event
        
        # Check if old prep/debrief still exist (they shouldn't)
        elif (abs((event_start - original_prep_start).total_seconds()) < 300 and
              "prep" in event_title):
            old_prep_found = True
        elif (abs((event_start - original_debrief_start).total_seconds()) < 300 and
              "debrief" in event_title):
            old_debrief_found = True
    
    check_logs = []
    
    # Validate results
    if not main_meeting:
        check_logs.append({"name":"main_meeting_check","verdict": False,"reason":"Main meeting not found at new time - external partner controls this"})
    else:
        check_logs.append({"name":"main_meeting_check","status":"passed","reason":"Main meeting found at new time"})
    
    if old_prep_found:
        check_logs.append({"name":"old_prep_check","verdict": False,"reason":"Prep meeting still at original time - cascade failed"})
    else:
        check_logs.append({"name":"old_prep_check","status":"passed","reason":""})
    
    if old_debrief_found:
        check_logs.append({"name":"old_debrief_check","verdict": False,"reason":"Debrief meeting still at original time - cascade failed"})
    else:
        check_logs.append({"name":"old_debrief_check","status":"passed","reason":""})
    
    if not prep_meeting:
        check_logs.append({"name":"prep_meeting_check","verdict": False,"reason":"Prep meeting not found at new time - should be 15 min before main"})
    else:
        check_logs.append({"name":"prep_meeting_check","status":"passed","reason":"Prep meeting found at new time"})
    
    if not debrief_meeting:
        check_logs.append({"name":"debrief_meeting_check","verdict": False,"reason":"Debrief meeting not found at new time - should be right after main"})
    else:
        check_logs.append({"name":"debrief_meeting_check","status":"passed","reason":"Debrief meeting found at new time"})
    
    # Determine overall success
    overall_success = all(cl["status"] == "passed" for cl in check_logs)
        
    return overall_success, check_logs


# The validation function is available as 'validation_function'
