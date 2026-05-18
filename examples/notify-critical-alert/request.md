# Notify Critical Alert Request

Post a critical alert to the #incidents Slack channel when the system detects a P0 issue.

Constraints:

- Target channel: #incidents.
- Message must include severity, affected service, and a runbook link.
- Do not send DMs.
- Do not create additional Slack channels.
- Rollback: delete the message if posted within 5 minutes.
