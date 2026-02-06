"""
Verifier for scenario scenario_004_meeting_modification
Generated on 2026-02-04T11:20:02.174778
"""


from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Tuple

from gordon import TaskVerifier

def validation_function(state: Dict[str, Any]) -> Tuple[float, List[TaskVerifier]]:
    """
    Standalone validation function for meeting modification scenario.
    
    Checks if meeting was updated with new location and additional guests, no conflicts.
    """
    # Hardcoded expected values
    expected_email = {
    "id": "email_9717",
    "threadId": "thread_4974",
    "subject": "Planning Meeting: Project X \u2014 Alignment & Next Steps",
    "body": "Hi Arjun, Ethan, and Grace,\n\nI\u2019d like to schedule a meeting to align on Project X. Meeting Title: Planning Meeting: Project X.\n\nObjectives:\n- Confirm project scope and success criteria\n- Finalize high-level timeline and key milestones\n- Identify dependencies and risks\n- Assign immediate next steps and owners\n\nProposed agenda (approx. 1 hour total):\n- 10 min: Quick introductions and objectives\n- 25 min: Scope review and priority discussion\n- 15 min: Timeline, milestones, and dependencies\n- 10 min: Action items, owners, and next steps\n\nLocation: Meeting Room 1\nEstimated duration: Approximately 1 hour\n\nAlan (alan@helixgrid.com), could you please find a suitable time for all of us within the next week and schedule this meeting in Meeting Room 1? Please coordinate with the team and propose times that work for everyone. \n\nIf you have any materials or items to add to the agenda, please share them in advance so we can include them in the meeting invite.\n\nThanks,\nCamila Ruiz",
    "snippet": "Hi Arjun, Ethan, and Grace,\n\nI\u2019d like to schedule a meeting to align on Project X. Meeting Title: Pl",
    "from": {
        "name": "Camila Ruiz",
        "email": "camila.ruiz@helixgrid.com"
    },
    "to": [
        {
            "name": "Alan Cooper",
            "email": "alan@helixgrid.com"
        }
    ],
    "cc": [
        {
            "name": "Arjun Iyer",
            "email": "arjun.iyer@talentspring.co"
        },
        {
            "name": "Ethan Park",
            "email": "ethan.park@helixgrid.com"
        },
        {
            "name": "Grace Nguyen",
            "email": "grace.nguyen@helixgrid.com"
        }
    ],
    "bcc": [],
    "timestamp": "2026-01-21T19:20:00Z",
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
    expected_new_location = "Conference Room D"
    expected_additional_guest_emails = ['marcus.lee@helixgrid.com', 'diego.alvarez@helixgrid.com']
    expected_meeting_title = 'Planning Meeting: Project X'
    
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
    
    # Extract original email participants
    email_participants = (
        {expected_email["from"]["email"]} |
        {cc["email"] for cc in expected_email["cc"]}
    )
    
    # Expected final participants (original + additional guests)
    expected_all_participants = email_participants | set(expected_additional_guest_emails)
    
    # Search for matching event
    event_found = False
    location_match = False
    all_participants_present = False
    participant_availability_dict = {
        k: True for k in expected_all_participants
    }
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
            if expected_new_location == "Google Meet":
                # Check for Google Meet via conferenceData
                conference_data = event.get("conferenceData", {})
                conference_solution = conference_data.get("conferenceSolution", {})
                location_match = conference_solution.get("name") == "Google Meet"
            elif expected_new_location:
                # Check physical location via location field
                location_match = expected_new_location in event.get("location", "")
            else:
                location_match = True
            
            # Check participants (original + additional guests)
            event_attendees = {
                attendee["email"]
                for attendee in event.get("attendees", [])
            }
            all_participants_present = (
                expected_all_participants.issubset(event_attendees)
            )
            
            # Check for participant conflicts
            # Parse event times (in UTC format)
            event_start = datetime.fromisoformat(event["start"].replace('Z', '+00:00').replace('.000+00:00', '+00:00'))
            if event_start.tzinfo is None:
                event_start = event_start.replace(tzinfo=timezone.utc)
            event_end = datetime.fromisoformat(event["end"].replace('Z', '+00:00').replace('.000+00:00', '+00:00'))
            if event_end.tzinfo is None:
                event_end = event_end.replace(tzinfo=timezone.utc)
            
            for participant_email in expected_all_participants:
                other_events = state.get('calendar-clone', {}).get(
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
    
    # Check 2: Location updated
    if event_found:
        checks.append(TaskVerifier(
            name="location_update_check",
            verdict=location_match,
            reason=f"Event location successfully updated to {expected_new_location}" if location_match else
                   f"Event location not updated to {expected_new_location}"
        ))
    else:
        checks.append(TaskVerifier(
            name="location_update_check",
            verdict=False,
            reason="Cannot check location - event not found"
        ))
    
    # Check 3: All participants added
    if event_found:
        if all_participants_present:
            checks.append(TaskVerifier(
                name="participants_check",
                verdict=True,
                reason="All participants including new guests added to event"
            ))
        else:
            event_attendees = {
                attendee["email"]
                for attendee in matching_event.get("attendees", [])
            } if matching_event else set()
            missing = expected_all_participants - event_attendees
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
    
    # Calculate reward: each check is worth 1/3
    passed_checks = sum(1 for c in checks if c.verdict)
    reward = passed_checks / len(checks) if checks else 0.0
    
    return reward, checks


# The validation function is available as 'validation_function'
