"""
Verifier for scenario scenario_006_conflict_detection
Generated on 2026-02-05T22:37:18.036539
"""


from typing import Dict, Any, List, Tuple

from gordon import TaskVerifier

def validation_function(state: Dict[str, Any]) -> Tuple[float, List[TaskVerifier]]:
    """
    Standalone validation function for conflict detection scenario.
    
    Checks if the agent detected the conflict and replied all to the original email thread.
    """
    # Hardcoded expected values
    thread_id = "thread_8383"
    organizer_email = "simon.walker@securemesh.io"
    expected_cc_emails = ['kaito.nakamura@helixgrid.com', 'elliot.rivera@gmail.com', 'priya.singh@helixgrid.com', 'olivia.brooks@helixgrid.com']
    user_email = "alan@helixgrid.com"
    
    emails = state.get('gmail-clone', {}).get('emails', [])
    thread_emails = [email for email in emails if email['threadId'] == thread_id]
    
    checks: List[TaskVerifier] = []
    
    # Find reply emails from the user
    user_reply_found = False
    reply_all_verified = False
    organizer_in_to = False
    cc_preserved = False
    
    for email in thread_emails:
        if 'SENT' in email.get('labels', []) and email['from']['email'] == user_email:
            user_reply_found = True
            
            # Check if this is a proper Reply All
            # Should include organizer in 'to' and all original CC recipients in 'cc'
            to_emails = [recipient['email'] for recipient in email.get('to', [])]
            cc_emails = [recipient['email'] for recipient in email.get('cc', [])]
            
            # Verify organizer is in 'to' field
            organizer_in_to = organizer_email in to_emails
            
            # Verify all original CC recipients are still in CC (minus the user themselves)
            original_cc_set = set(expected_cc_emails) - {user_email}
            reply_cc_set = set(cc_emails)
            cc_preserved = original_cc_set.issubset(reply_cc_set)
            
            if organizer_in_to and cc_preserved:
                reply_all_verified = True
                break
    
    # Check 1: User reply found
    checks.append(TaskVerifier(
        name="user_reply_check",
        verdict=user_reply_found,
        reason="Reply email found from user in the thread" if user_reply_found else
               "No reply email found from user in the thread"
    ))
    
    # Check 2: Organizer in 'to' field
    if user_reply_found:
        checks.append(TaskVerifier(
            name="organizer_recipient_check",
            verdict=organizer_in_to,
            reason="Organizer included in 'to' field" if organizer_in_to else
                   f"Organizer {organizer_email} not in 'to' field"
        ))
    else:
        checks.append(TaskVerifier(
            name="organizer_recipient_check",
            verdict=False,
            reason="Cannot check recipients - no reply found"
        ))
    
    # Check 3: CC recipients preserved
    if user_reply_found:
        checks.append(TaskVerifier(
            name="cc_recipients_check",
            verdict=cc_preserved,
            reason="All original CC recipients preserved" if cc_preserved else
                   "Not all original CC recipients included in reply"
        ))
    else:
        checks.append(TaskVerifier(
            name="cc_recipients_check",
            verdict=False,
            reason="Cannot check CC recipients - no reply found"
        ))
    
    # Check 4: Overall Reply All verification
    checks.append(TaskVerifier(
        name="reply_all_check",
        verdict=reply_all_verified,
        reason="Reply All used correctly" if reply_all_verified else
               "Reply was not sent to all original recipients (Reply All not used)"
    ))
    
    # Calculate reward: each check is worth 1/4
    passed_checks = sum(1 for c in checks if c.verdict)
    reward = passed_checks / len(checks) if checks else 0.0
    
    return reward, checks


# The validation function is available as 'validation_function'
