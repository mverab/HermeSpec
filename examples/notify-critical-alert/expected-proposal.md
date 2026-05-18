# Notify team of critical alert

## Summary

Post critical alert to Slack #incidents.

## Contract Type

`external_action`

## Approval

Approval is required before execution.

## Required Contract Payload

- Objective: Notify on-call engineers of a P0 issue via Slack.
- Action: Send a message to #incidents with severity, affected service, and runbook link.
- Audience: On-call engineers.
- Channel: Slack.
- Approval: Required with at least one approver.
- Constraints: No DMs, no new channels, message deletion rollback within 5 minutes.
- Rollback: Delete the posted message if within 5 minutes.
- Acceptance criteria:
  - Message is posted to #incidents within 30 seconds.
  - Message includes severity, affected service, and runbook link.
