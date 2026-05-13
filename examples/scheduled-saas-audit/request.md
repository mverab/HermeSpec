# Scheduled SaaS Audit Request

Every Monday at 9:00 AM America/Merida, audit SaaS subscriptions and alert if spend increases more than 15%.

Constraints:

- Read-only execution.
- Do not cancel subscriptions.
- Do not contact vendors.
- Report through Telegram.
- Include measured current spend, prior baseline spend, and the observed percentage change in the transcript.
