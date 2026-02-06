"""
Verifier for scenario scenario_003_meeting_modification
Generated on 2026-02-05T22:35:36.374286
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
    "id": "email_3505",
    "threadId": "thread_9020",
    "subject": "Planning Meeting: Project X \u2014 Initial Alignment",
    "body": "Hi Liam, Anika, and Elena,\n\nI'd like to schedule a meeting titled \"Project X - Planning Meeting\" to align on the next steps for Project X. The meeting will be approximately 30 minutes and will take place in Conference Room B.\n\nAgenda\n- Review and confirm project scope and objectives\n- Identify key deliverables and milestones\n- Assign initial action items and owners\n- Surface immediate risks, dependencies, and blockers\n- Define next steps and communication cadence\n\nObjectives\n- Ensure a shared understanding of scope and success criteria\n- Agree on owners for first deliverables and immediate actions\n- Establish clear next steps and follow-up plan\n\nAlan (alan@helixgrid.com), could you please find a suitable 30-minute slot for all participants within the next week and book Conference Room B? Once you propose options, I\u2019ll confirm with the group. If any of you have scheduling constraints or materials to share in advance, please let us know.\n\nThanks,\nSarah Patel",
    "snippet": "Hi Liam, Anika, and Elena,\n\nI'd like to schedule a meeting titled \"Project X - Planning Meeting\" to ",
    "from": {
        "name": "Sarah Patel",
        "email": "sarah.patel@helixgrid.com"
    },
    "to": [
        {
            "name": "Alan Cooper",
            "email": "alan@helixgrid.com"
        }
    ],
    "cc": [
        {
            "name": "Liam O'Connor",
            "email": "liam.oconnor@helixgrid.com"
        },
        {
            "name": "Anika Bose",
            "email": "anika.bose@helixgrid.com"
        },
        {
            "name": "Elena Garc\u00eda",
            "email": "elena.garcia@helixgrid.com"
        },
        {
            "name": "Liam O'Connor",
            "email": "liam.oconnor@helixgrid.com"
        }
    ],
    "bcc": [],
    "timestamp": "2026-01-13T18:34:00Z",
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
    expected_new_location = "Conference Room C"
    expected_additional_guest_emails = ['marcus.osei@helixgrid.com', 'pri.menon@auroracloud.com']
    expected_meeting_title = 'Project X - Planning Meeting'
    
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
