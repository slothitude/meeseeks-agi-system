# Google API Setup for Sloth_rog

**Date:** 2026-03-06
**Purpose:** Secure API access to Google services

---

## What We're Setting Up

| Service | API | What I Can Do |
|---------|-----|---------------|
| **Gmail** | Gmail API | Read/send emails, manage inbox |
| **Drive** | Drive API | Create/edit files, organize folders |
| **Calendar** | Calendar API | Schedule events, reminders |
| **YouTube** | YouTube Data API | Manage channel, analytics |
| **Gemini** | Gemini API | Direct AI access |

---

## Setup Steps

### Step 1: Create Google Cloud Project

1. Go to: https://console.cloud.google.com/
2. Create new project: "sloth-rog-agi"
3. Note the project ID

### Step 2: Enable APIs

In the project, enable:
- Gmail API
- Google Drive API
- Google Calendar API
- YouTube Data API v3
- (Optional) Gemini API

### Step 3: Create Credentials

**Option A: OAuth 2.0 (User Access)**
- Create OAuth consent screen
- Create OAuth 2.0 client ID (Desktop app)
- Download credentials.json
- First use requires browser auth (you approve)

**Option B: Service Account (Bot Access)**
- Create service account
- Download JSON key
- No browser auth needed
- Share specific resources with service account email

**Recommendation:** Start with OAuth 2.0, you stay in control

### Step 4: Configure in OpenClaw

Save credentials to: `~/.openclaw/google_credentials.json`

Or add to OpenClaw config:
```json
{
  "google": {
    "credentials_path": "path/to/credentials.json",
    "token_path": "path/to/token.json"
  }
}
```

---

## Security Benefits

✅ **No password sharing** - OAuth tokens can be revoked
✅ **Scoped access** - Only specific APIs enabled
✅ **Audit trail** - All API calls logged
✅ **Revocable** - You can disconnect anytime
✅ **Rate limited** - Prevents abuse

---

## Quick Start (Minimal Setup)

For just viewing Gemini shared links:
1. Create project
2. Enable Gemini API
3. Create API key
4. Paste key here

That's it - no OAuth needed for public shared links with API key.

---

## What I Need From You

1. **Google Cloud project created?** (yes/no)
2. **Which APIs enabled?** (gmail, drive, calendar, youtube, gemini)
3. **Credentials type?** (OAuth or Service Account)
4. **Credentials file** (paste contents or tell me where to find it)

---

Let me know when you've created the project and I'll guide you through the next steps! 🦥
