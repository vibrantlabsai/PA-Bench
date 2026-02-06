"""
Verifier for scenario scenario_009_meeting_cancellation
Generated on 2026-02-05T22:39:15.147834
"""


from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Tuple

from gordon import TaskVerifier

def validation_function(state: Dict[str, Any]) -> Tuple[float, List[TaskVerifier]]:
    """
    Standalone validation function for meeting cancellation scenario.
    
    Checks if meeting was deleted and cancellation emails were sent.
    """
    # Hardcoded expected values
    expected_event = {
    "title": "Project X Planning Meeting",
    "description": "",
    "calendarId": "primary",
    "start": "2026-01-13T00:00:00Z",
    "end": "2026-01-13T00:30:00Z",
    "location": "Conference Room B",
    "attendees": [
        {
            "email": "alan@helixgrid.com",
            "name": "Alan Cooper",
            "isOrganizer": True,
            "responseStatus": "accepted",
            "isSelf": False
        },
        {
            "email": "priyanka.rao@helixgrid.com",
            "name": "Priyanka Rao",
            "isOrganizer": False,
            "responseStatus": "needsAction",
            "isSelf": False
        },
        {
            "email": "yara.haddad@helixgrid.com",
            "name": "Yara Haddad",
            "isOrganizer": False,
            "responseStatus": "needsAction",
            "isSelf": False
        },
        {
            "email": "ethan.park@ridgeviewadvisors.com",
            "name": "Ethan Park",
            "isOrganizer": False,
            "responseStatus": "needsAction",
            "isSelf": False
        },
        {
            "email": "priya.singh@helixgrid.com",
            "name": "Priya Singh",
            "isOrganizer": False,
            "responseStatus": "needsAction",
            "isSelf": False
        }
    ],
    "id": "event_2029",
    "conferenceData": None,
    "status": "confirmed",
    "busyStatus": "busy",
    "isAllDay": False
}
    target_date = '2026-01-09T19:08:00.000Z'
    
    events = state.get("calendar-clone").get("events", [])
    emails = state.get("gmail-clone").get("emails", [])
    checks: List[TaskVerifier] = []
    
    # Check 1: Event removed from calendar
    event_exists = any(event.get("id") == expected_event["id"] for event in events)
    
    checks.append(TaskVerifier(
        name="event_removed_check",
        verdict=not event_exists,
        reason="Event successfully removed from calendar" if not event_exists else
               "Event still exists in calendar - cancellation not processed"
    ))
    
    # Check 2: Cancellation emails sent
    # Parse target date (in UTC format)
    target_date_obj = datetime.fromisoformat(target_date.replace('Z', '+00:00')).date()
    sent_emails = [
        email for email in emails 
        if 'SENT' in email.get("labels", []) and 
        datetime.fromisoformat(email["timestamp"].replace('Z', '+00:00').replace('.000+00:00', '+00:00')).date() == target_date_obj
    ]
    
    checks.append(TaskVerifier(
        name="emails_sent_check",
        verdict=bool(sent_emails),
        reason=f"Found {len(sent_emails)} email(s) sent on target date" if sent_emails else
               "No emails sent on the target date"
    ))
    
    # Check 3: Cancellation keywords in emails
    cancellation_email_found = False
    if sent_emails:
        for email in sent_emails:
            email_content = (email.get("subject", "") + " " + email.get("body", "")).lower()
            cancellation_keywords = ['cancel', 'cancellation', 'cancelled']
            
            if any(keyword in email_content for keyword in cancellation_keywords):
                cancellation_email_found = True
                break
        
        checks.append(TaskVerifier(
            name="cancellation_keyword_check",
            verdict=cancellation_email_found,
            reason="Cancellation-related email found in sent items" if cancellation_email_found else
                   "No cancellation-related emails found in sent items"
        ))
    else:
        checks.append(TaskVerifier(
            name="cancellation_keyword_check",
            verdict=False,
            reason="Cannot check keywords - no emails sent"
        ))
    
    # Calculate reward: each check is worth 1/3
    passed_checks = sum(1 for c in checks if c.verdict)
    reward = passed_checks / len(checks) if checks else 0.0
    
    return reward, checks


# The validation function is available as 'validation_function'
