"""
Verifier for scenario scenario_015_meeting_scheduling
Generated on 2026-02-05T22:41:21.486918
"""


from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Tuple

from gordon import TaskVerifier

def validation_function(state: Dict[str, Any]) -> Tuple[float, List[TaskVerifier]]:
    """
    Standalone validation function for meeting scheduling scenario.
    
    Checks if a meeting was scheduled correctly based on email request.
    """
    # Hardcoded expected values (no external dependencies)
    expected_email = {
    "id": "email_7055",
    "threadId": "thread_8788",
    "from": {
        "name": "Ravi Sharma",
        "email": "ravi.sharma@helixgrid.com"
    },
    "to": [
        {
            "name": "Alan Cooper",
            "email": "alan@helixgrid.com"
        }
    ],
    "cc": [
        {
            "name": "Anika Bose",
            "email": "anika.bose@helixgrid.com"
        },
        {
            "name": "Laura Bennett",
            "email": "laura.bennett@helixgrid.com"
        }
    ],
    "bcc": [],
    "subject": "Planning Meeting: Project X \u2014 Scope & Next Steps",
    "body": "Hi Anika, Laura, and Alan,\n\nI\u2019d like to schedule a meeting titled \"Project X \u2014 Planning & Alignment\" to align on scope, outstanding issues, and next steps for Project X. The meeting will be held via Google Meet and should be approximately 30 minutes.\n\nAgenda:\n- Quick status update on Project X\n- Confirm scope and key deliverables\n- Identify blockers and resource needs\n- Assign owners and agree immediate next steps\n\nObjectives:\n- Ensure everyone has a shared understanding of current priorities\n- Resolve any immediate blockers or clarify dependencies\n- Assign action items with owners and target milestones\n- Schedule follow-up checkpoints as needed\n\nAlan (alan@helixgrid.com), could you please find a suitable 30-minute slot on Google Meet within the next week that works for all of us and send the calendar invite? Anika and Laura, please reply with any additional agenda items or constraints on your availability.\n\nThanks,\nRavi Sharma",
    "snippet": "Hi Anika, Laura, and Alan,\n\nI\u2019d like to schedule a meeting titled \"Project X \u2014 Planning & Alignment\"",
    "timestamp": "2026-01-20T20:47:00Z",
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
    expected_meeting_title = 'Project X — Planning & Alignment'
    
    events = state.get("gocalendar").get("events", [])

    # Calculate email week boundaries
    email_timestamp = datetime.fromisoformat(expected_email["timestamp"])
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
    location_match = True
    all_participants_present = False
    participant_availability_dict = {
        k: True for k in email_participants
    }
    event_attendees = set()

    for event in events:
        event_start_dt = datetime.fromisoformat(event["start"])
        if event_start_dt.tzinfo is None:
            event_start_dt = event_start_dt.replace(tzinfo=timezone.utc)
        event_date = event_start_dt.date()

        # Check if event matches criteria
        if (event["title"] == expected_meeting_title and
                week_start <= event_date <= week_end):

            event_found = True

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
            event_start = datetime.fromisoformat(event["start"])
            if event_start.tzinfo is None:
                event_start = event_start.replace(tzinfo=timezone.utc)
            event_end = datetime.fromisoformat(event["end"])
            if event_end.tzinfo is None:
                event_end = event_end.replace(tzinfo=timezone.utc)

            for participant_email in email_participants:
                other_events = state.get(
                    "otherUsersEvents", {}
                ).get(participant_email, [])
                for other_event in other_events:
                    other_start = datetime.fromisoformat(
                        other_event["start"]
                    )
                    if other_start.tzinfo is None:
                        other_start = other_start.replace(tzinfo=timezone.utc)
                    other_end = datetime.fromisoformat(
                        other_event["end"]
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

    checks: List[TaskVerifier] = []
    
    # Check 1: Event found
    checks.append(TaskVerifier(
        name="event_found_check",
        verdict=event_found,
        reason=f"Event '{expected_meeting_title}' found within week {week_start} to {week_end}" if event_found else
               f"No matching event found for meeting title '{expected_meeting_title}' within week {week_start} to {week_end}"
    ))
    
    # Check 2: Location match
    if event_found:
        checks.append(TaskVerifier(
            name="location_match_check",
            verdict=location_match,
            reason="Event location matches the specified location" if location_match else
                   f"Event location does not match the specified location '{expected_location}'"
        ))
    else:
        checks.append(TaskVerifier(
            name="location_match_check",
            verdict=False,
            reason="Cannot check location - event not found"
        ))
    
    # Check 3: All participants present
    if event_found:
        if all_participants_present:
            checks.append(TaskVerifier(
                name="participants_present_check",
                verdict=True,
                reason="All required participants included in event"
            ))
        else:
            missing = email_participants - event_attendees
            checks.append(TaskVerifier(
                name="participants_present_check",
                verdict=False,
                reason=f"Missing participants in event: {', '.join(missing)}"
            ))
    else:
        checks.append(TaskVerifier(
            name="participants_present_check",
            verdict=False,
            reason="Cannot check participants - event not found"
        ))
    
    # Check 4: No conflicts
    if event_found:
        unavailable = [
            email for email, available
            in participant_availability_dict.items()
            if not available
        ]
        checks.append(TaskVerifier(
            name="no_conflicts_check",
            verdict=not bool(unavailable),
            reason="All participants are available with no conflicts" if not unavailable else
                   f"Conflicts found for participants: {', '.join(unavailable)}"
        ))
    else:
        checks.append(TaskVerifier(
            name="no_conflicts_check",
            verdict=False,
            reason="Cannot check conflicts - event not found"
        ))
    
    # Calculate reward: each check is worth 1/4
    passed_checks = sum(1 for c in checks if c.verdict)
    reward = passed_checks / len(checks) if checks else 0.0
    
    return reward, checks


# The validation function is available as 'validation_function'
