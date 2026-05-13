# Audit SaaS subscriptions weekly

## Summary

Audit SaaS spend every Monday and alert if it increases more than 15%.

## Contract Type

`scheduled_task`

## Approval

Approval is required before execution.

## Required Contract Payload

- Objective: Audit SaaS subscriptions weekly and alert only when spend increases more than 15%.
- Trigger: Cron `0 9 * * MON` in `America/Merida`.
- Preconditions: Billing exports and prior baseline are available before execution.
- Actions: Read SaaS billing data, compare current spend with the approved baseline, and send a Telegram alert only if the threshold is crossed.
- Idempotency: Use the ISO week start date as the dedupe key.
- Rollback: Read-only task; no state rollback is required.
- Alerting: Telegram for threshold crossings and failures.
- Acceptance criteria:
  - Current spend and prior baseline are both reported.
  - Observed spend increase percentage is computed.
  - Telegram alert is sent only when observed increase is greater than 15%.
  - Transcript includes acceptance evidence before Hermes claims completion.
