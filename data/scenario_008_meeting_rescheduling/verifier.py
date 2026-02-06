"""
Verifier for scenario scenario_008_meeting_rescheduling
Generated on 2026-02-04T11:23:21.695610
"""


from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Tuple

from gordon import TaskVerifier

def validation_function(state: Dict[str, Any]) -> Tuple[float, List[TaskVerifier]]:
    """
    Standalone validation function for meeting rescheduling scenario.
    
    Checks if meeting exists one week from original email and no participants have conflicts.
    """
    # Hardcoded expected values
    expected_email = {
    "id": "email_9547",
    "threadId": "thread_6015",
    "subject": "Planning Meeting: Sprint Priorities & Launch Readiness",
    "body": "Hi Simon, Rhea, and Lydia,\n\nI\u2019d like to schedule a meeting titled \u201cSprint Priorities & Launch Readiness\u201d to align on our next sprint and ensure we\u2019re ready for the upcoming launch.\n\nObjectives:\n- Align on sprint priorities and confirm scope\n- Assign owners for remaining launch tasks\n- Identify and mitigate any blockers or risks\n- Agree on timeline and next steps leading up to launch\n\nProposed agenda (45 minutes):\n1. Quick status update (5\u20137 min)\n2. Review and prioritize backlog items for the sprint (15 min)\n3. Assign tasks and owners (10 min)\n4. Identify risks/blockers and mitigation plans (8 min)\n5. Confirm timeline and next steps (5 min)\n\nMeeting details:\n- Meeting title: Sprint Priorities & Launch Readiness\n- Duration: approximately 45 minutes\n- Location: Google Meet\n\nAlan (alan@helixgrid.com), could you please find a suitable time for all and schedule this meeting on Google Meet for this week? Everyone else, please reply with your availability for this week or let us know if you need a different week.\n\nThanks,\nOmar Hassan",
    "snippet": "Hi Simon, Rhea, and Lydia,\n\nI\u2019d like to schedule a meeting titled \u201cSprint Priorities & Launch Readin",
    "from": {
        "name": "Omar Hassan",
        "email": "omar.hassan@helixgrid.com"
    },
    "to": [
        {
            "name": "Alan Cooper",
            "email": "alan@helixgrid.com"
        }
    ],
    "cc": [
        {
            "name": "Simon Walker",
            "email": "simon.walker@securemesh.io"
        },
        {
            "name": "Rhea Patel",
            "email": "rhea@peakspr.com"
        },
        {
            "name": "Lydia Chen",
            "email": "lydia.chen@logpulse.ai"
        }
    ],
    "bcc": [],
    "timestamp": "2026-01-06T19:58:00Z",
    "isRead": False,
    "isStarred": False,
    "labels": [
        "INBOX"
    ],
    "hasAttachments": False,
    "attachments": [],
    "isImportant": False,
    "category": None,
    "isVerifiedSender": None,
    "reactions": [],
    "quotedContent": None,
    "hasQuotedContent": None
}
    expected_location = 'Google Meet'
    expected_meeting_title = 'Sprint Priorities & Launch Readiness'
    
    events = state.get("calendar-clone").get("events", [])
    checks: List[TaskVerifier] = []
    
    # Calculate email week boundaries
    # Parse email timestamp (in UTC format)
    email_timestamp = datetime.fromisoformat(expected_email["timestamp"].replace('Z', '+00:00'))
    if email_timestamp.tzinfo is None:
        email_timestamp = email_timestamp.replace(tzinfo=timezone.utc)
    email_date = email_timestamp.date()
    # Meeting should be scheduled from email date onwards, extending into next week if needed
    week_start = email_date  # Start from when email was sent
    week_end = email_date + timedelta(days=7)  # Allow 7 days from email date
    
    # Extract email participants
    email_participants = (
        {expected_email["from"]["email"]} |
        {cc["email"] for cc in expected_email["cc"]}
    )
    
    # Search for matching event
    event_found = False
    location_match = False
    all_participants_present = False
    participant_availability_dict = {
        k: True for k in email_participants
    }
    event_attendees = set()
    matching_event = None
    
    for event in events:
        # Parse event start time (in UTC format)
        event_start_dt = datetime.fromisoformat(event["start"].replace('Z', '+00:00').replace('.000+00:00', '+00:00'))
        if event_start_dt.tzinfo is None:
            event_start_dt = event_start_dt.replace(tzinfo=timezone.utc)
        event_date = event_start_dt.date()
        
        # Check if event matches criteria
        if (event["title"] == expected_meeting_title and
                week_start <= event_date <= week_end):
            
            event_found = True
            matching_event = event
            
            # Check location match
            if expected_location == "Google Meet":
                # Check for Google Meet via conferenceData
                conference_data = event.get("conferenceData", {})
                conference_solution = conference_data.get("conferenceSolution", {})
                location_match = conference_solution.get("name") == "Google Meet"
            elif expected_location:
                # Check physical location via location field
                location_match = expected_location in event.get("location", "")
            else:
                location_match = True
            
            # Check participants
            event_attendees = {
                attendee["email"]
                for attendee in event.get("attendees", [])
            }
            all_participants_present = (
                email_participants.issubset(event_attendees)
            )
            
            # Check for participant conflicts
            # Parse event times (in UTC format)
            event_start = datetime.fromisoformat(event["start"].replace('Z', '+00:00').replace('.000+00:00', '+00:00'))
            if event_start.tzinfo is None:
                event_start = event_start.replace(tzinfo=timezone.utc)
            event_end = datetime.fromisoformat(event["end"].replace('Z', '+00:00').replace('.000+00:00', '+00:00'))
            if event_end.tzinfo is None:
                event_end = event_end.replace(tzinfo=timezone.utc)
            
            for participant_email in email_participants:
                other_events = state.get(
                    "otherUsersEvents", {}
                ).get(participant_email, [])
                for other_event in other_events:
                    other_start = datetime.fromisoformat(
                        other_event["start"].replace('Z', '+00:00').replace('.000+00:00', '+00:00')
                    )
                    if other_start.tzinfo is None:
                        other_start = other_start.replace(tzinfo=timezone.utc)
                    other_end = datetime.fromisoformat(
                        other_event["end"].replace('Z', '+00:00').replace('.000+00:00', '+00:00')
                    )
                    if other_end.tzinfo is None:
                        other_end = other_end.replace(tzinfo=timezone.utc)
                    
                    # Check for time overlap (excluding same event)
                    if (other_event["id"] != event["id"] and
                            event_start < other_end and
                            event_end > other_start):
                        participant_availability_dict[
                            participant_email
                        ] = False
            break
    
    # Check 1: Event found
    checks.append(TaskVerifier(
        name="event_found_check",
        verdict=event_found,
        reason=f"Found meeting '{expected_meeting_title}' scheduled within valid timeframe" if event_found else
               f"No matching event found for '{expected_meeting_title}' between {week_start} and {week_end}"
    ))
    
    # Check 2: Location match
    if event_found:
        checks.append(TaskVerifier(
            name="location_check",
            verdict=location_match,
            reason=f"Event location matches expected location: {expected_location}" if location_match else
                   f"Event location does not match expected location: {expected_location}"
        ))
    else:
        checks.append(TaskVerifier(
            name="location_check",
            verdict=False,
            reason="Cannot check location - event not found"
        ))
    
    # Check 3: All participants present
    if event_found:
        if all_participants_present:
            checks.append(TaskVerifier(
                name="participants_check",
                verdict=True,
                reason="All required participants are included in the event"
            ))
        else:
            missing = email_participants - event_attendees
            checks.append(TaskVerifier(
                name="participants_check",
                verdict=False,
                reason=f"Missing participants: {', '.join(missing)}"
            ))
    else:
        checks.append(TaskVerifier(
            name="participants_check",
            verdict=False,
            reason="Cannot check participants - event not found"
        ))
    
    # Check 4: No scheduling conflicts
    unavailable = [
        email for email, available
        in participant_availability_dict.items()
        if not available
    ]
    if event_found:
        checks.append(TaskVerifier(
            name="conflict_check",
            verdict=not bool(unavailable),
            reason="All participants are available with no scheduling conflicts" if not unavailable else
                   f"Scheduling conflicts found for: {', '.join(unavailable)}"
        ))
    else:
        checks.append(TaskVerifier(
            name="conflict_check",
            verdict=False,
            reason="Cannot check conflicts - event not found"
        ))
    
    # Calculate reward: each check is worth 1/4
    passed_checks = sum(1 for c in checks if c.verdict)
    reward = passed_checks / len(checks) if checks else 0.0
    
    return reward, checks


# The validation function is available as 'validation_function'
