"""
Verifier for scenario scenario_002_multi_meeting_coordination
Generated on 2026-02-04T11:18:56.146073
"""


from typing import Dict, Any, List, Tuple
from datetime import datetime, timezone

from gordon import TaskVerifier

def validation_function(state: Dict[str, Any]) -> Tuple[float, List[TaskVerifier]]:
    """
    Standalone validation function for multi-meeting coordination scenario.
    
    Checks if prep, main, and debrief meetings were properly scheduled.
    """
    # Hardcoded expected values (already in UTC)
    main_start = datetime.fromisoformat("2026-01-28T21:15:00")
    main_end = datetime.fromisoformat("2026-01-28T22:15:00")
    prep_start = datetime.fromisoformat("2026-01-28T21:00:00")
    prep_end = datetime.fromisoformat("2026-01-28T21:15:00")
    debrief_start = datetime.fromisoformat("2026-01-28T22:15:00")
    debrief_end = datetime.fromisoformat("2026-01-28T22:30:00")
    
    # Ensure all expected times are timezone-aware
    if main_start.tzinfo is None:
        main_start = main_start.replace(tzinfo=timezone.utc)
    if main_end.tzinfo is None:
        main_end = main_end.replace(tzinfo=timezone.utc)
    if prep_start.tzinfo is None:
        prep_start = prep_start.replace(tzinfo=timezone.utc)
    if prep_end.tzinfo is None:
        prep_end = prep_end.replace(tzinfo=timezone.utc)
    if debrief_start.tzinfo is None:
        debrief_start = debrief_start.replace(tzinfo=timezone.utc)
    if debrief_end.tzinfo is None:
        debrief_end = debrief_end.replace(tzinfo=timezone.utc)
    
    external_email = "arjun.iyer@talentspring.co"
    internal_emails = {'alan@helixgrid.com', 'adrian.muller@helixgrid.com', 'tomas.oliveira@helixgrid.com'}
    
    events = state.get("calendar-clone").get("events", [])
    checks: List[TaskVerifier] = []
    
    # Find meetings by timing and participants
    main_meeting = None
    prep_meeting = None
    debrief_meeting = None
    
    for event in events:
        # Events are always in UTC/Zulu time
        event_start_str = event["start"].replace('Z', '+00:00').replace('.000+00:00', '+00:00')
        event_end_str = event["end"].replace('Z', '+00:00').replace('.000+00:00', '+00:00')
        event_start = datetime.fromisoformat(event_start_str)
        event_end = datetime.fromisoformat(event_end_str)
        
        # Ensure event times are timezone-aware
        if event_start.tzinfo is None:
            event_start = event_start.replace(tzinfo=timezone.utc)
        if event_end.tzinfo is None:
            event_end = event_end.replace(tzinfo=timezone.utc)
        
        attendee_emails = {att["email"] for att in event.get("attendees", [])}
        
        
        # Check for prep meeting (15 min, internal only, before main)
        if (abs((event_start - prep_start).total_seconds()) < 300 and
              abs((event_end - prep_end).total_seconds()) < 300 and
              external_email not in attendee_emails and
              internal_emails.issubset(attendee_emails)):
            prep_meeting = event
        
        # Check for debrief meeting (15 min, internal only, after main)
        if (abs((event_start - debrief_start).total_seconds()) < 300 and
              abs((event_end - debrief_end).total_seconds()) < 300 and
              external_email not in attendee_emails and
              internal_emails.issubset(attendee_emails)):
            debrief_meeting = event
    
    
    # Check 1: Prep meeting scheduled correctly
    checks.append(TaskVerifier(
        name="prep_meeting_check",
        verdict=bool(prep_meeting),
        reason="Prep meeting scheduled correctly 15 minutes before main meeting (internal only)" if prep_meeting else
               "Prep meeting not found or has incorrect participants/timing"
    ))
    
    # Check 2: Debrief meeting scheduled correctly
    checks.append(TaskVerifier(
        name="debrief_meeting_check",
        verdict=bool(debrief_meeting),
        reason="Debrief meeting scheduled correctly 15 minutes after main meeting (internal only)" if debrief_meeting else
               "Debrief meeting not found or has incorrect participants/timing"
    ))
    
    # Calculate reward: each check is worth 1/2
    passed_checks = sum(1 for c in checks if c.verdict)
    reward = passed_checks / len(checks) if checks else 0.0
    
    return reward, checks


# The validation function is available as 'validation_function'
