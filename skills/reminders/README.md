# OpenClaw Reminders

Working reminder system with dual messages.

## How It Works

1. **Cron job fires** → System event to main session
2. **Agent receives** → Full context (title, external, context)
3. **Agent relays** → Sends `EXTERNAL MESSAGE` to user Telegram

## Creating Reminders

Tell Sloth_rog:

```
"Remind me at 2pm to call Dave about the HHO project"
"Remind me in 30 minutes to check the oven"
"Set a reminder for tomorrow 9am: Team meeting"
```

### With Extra Context

```
"Remind me at 3pm to call Zane. Context: Samsung cord BN39-03006A, get Samsung to pay, order for Monday install."
```

- **You get:** `⏰ Call Zane`
- **Agent keeps:** Samsung cord details, payment info, deadline

## Reminder Format

Internal format (what the agent receives):

```
⏰ REMINDER: Call Dave about HHO project

EXTERNAL MESSAGE: "📞 Call Dave about the HHO remote display"

CONTEXT: Dave approved the project. Parts to order today from Jaycar + Altronics (~$178). Check projects/hho-display-box/ for details.
```

Agent sends only `EXTERNAL MESSAGE` to Telegram.

## Files

- `create_reminder.py` - Generate cron job config
- `handle_reminder.py` - Parse reminder when it fires
- `README.md` - This file

## Manual Creation

If you need to create via cron tool directly:

```json
{
  "name": "reminder-20260304-1400",
  "enabled": true,
  "deleteAfterRun": true,
  "schedule": {
    "kind": "at",
    "at": "2026-03-04T04:00:00.000Z"
  },
  "sessionTarget": "main",
  "wakeMode": "now",
  "payload": {
    "kind": "systemEvent",
    "text": "⏰ REMINDER: Your message\n\nEXTERNAL MESSAGE: \"Short version for user\"\n\nCONTEXT: Extra details for agent"
  }
}
```

Note: Schedule time is UTC (Brisbane -10 hours).
