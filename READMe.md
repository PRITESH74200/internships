# Gmail to Google Sheets Automation

**Author:** Pritesh Belgundi

A production-ready Python 3 application that automatically reads unread emails from Gmail and appends them to Google Sheets using OAuth 2.0 authentication. The system prevents duplicate processing through persistent state management and marks processed emails as read.

---

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Duplicate Prevention Strategy](#duplicate-prevention-strategy)
- [State Persistence](#state-persistence)
- [OAuth Flow](#oauth-flow)
- [Challenges & Solutions](#challenges--solutions)
- [Limitations](#limitations)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)

---

## ✨ Features

- **Real-time Gmail Integration**: Fetches unread emails from Gmail Inbox using Gmail API
- **Google Sheets Export**: Appends email data (From, Subject, Date, Content) to Google Sheets
- **OAuth 2.0 Authentication**: Secure authentication without service accounts
- **Duplicate Prevention**: Never reprocesses the same email twice
- **State Persistence**: Maintains processed email IDs across script executions
- **Mark as Read**: Automatically marks processed emails as read in Gmail
- **Plain Text Extraction**: Converts HTML emails to plain text
- **Error Handling**: Robust error handling with detailed logging
- **Production Ready**: Clean code, modular design, comprehensive documentation

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         MAIN ORCHESTRATOR                    │
│                          (main.py)                           │
└────────────┬──────────────────────────────────┬─────────────┘
             │                                   │
             ▼                                   ▼
    ┌────────────────┐                 ┌─────────────────┐
    │  Gmail Service │                 │ Sheets Service  │
    │ (gmail_service)│                 │(sheets_service) │
    └────────┬───────┘                 └────────┬────────┘
             │                                   │
             │  ┌──────────────────┐            │
             └─►│  Email Parser    │            │
                │ (email_parser)   │            │
                └──────────────────┘            │
                                                 │
    ┌────────────────────────────────────────────┘
    │
    ▼
┌───────────────────────────────────────────────────────────┐
│                   GOOGLE SHEETS SPREADSHEET               │
│  ┌──────────┬─────────────┬─────────────┬──────────────┐ │
│  │   From   │   Subject   │    Date     │   Content    │ │
│  ├──────────┼─────────────┼─────────────┼──────────────┤ │
│  │  email1  │   subject1  │  2026-01-13 │    body1     │ │
│  │  email2  │   subject2  │  2026-01-13 │    body2     │ │
│  └──────────┴─────────────┴─────────────┴──────────────┘ │
└───────────────────────────────────────────────────────────┘

    ┌────────────────────────────────────┐
    │      STATE PERSISTENCE FILE        │
    │     (processed_ids.json)           │
    │  ["msg_id1", "msg_id2", ...]       │
    └────────────────────────────────────┘
```

### Component Responsibilities

1. **main.py**: Orchestrates the entire workflow
2. **gmail_service.py**: Gmail OAuth, email fetching, marking as read
3. **email_parser.py**: Extracts sender, subject, date, and plain text body
4. **sheets_service.py**: Google Sheets OAuth and data appending
5. **config.py**: Centralized configuration and constants
6. **StateManager**: Tracks processed emails to prevent duplicates

---

## 📁 Project Structure

```
gmail-to-sheets/
│
├── src/
│   ├── gmail_service.py        # Gmail API operations
│   ├── sheets_service.py       # Google Sheets API operations
│   ├── email_parser.py         # Email parsing logic
│   └── main.py                 # Main orchestration script
│
├── credentials/
│   ├── credentials.json        # OAuth client secrets (NOT committed)
│   └── token.json              # OAuth tokens (auto-generated)
│
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
└── processed_ids.json          # State file (auto-generated)
```

---

## 🔧 Prerequisites

1. **Python 3.7+** installed
2. **Google Account** with Gmail access
3. **Google Cloud Project** with Gmail and Sheets APIs enabled
4. **OAuth 2.0 Credentials** downloaded from Google Cloud Console
5. **Google Sheet** created to store emails

---

## 📨 Why Gmail UI Can Show 0 Unread While API Returns More

- Gmail categories (Primary/Promotions/Social/Updates) can still hold unread items even when Primary looks clear.
- To align UI and API, we **explicitly filter INBOX + UNREAD** (`labelIds=['INBOX','UNREAD']` and query `is:unread label:INBOX`).
- After processing, we remove the `UNREAD` label via the Gmail API, so the next run sees 0 unread if the inbox is clear.

---

## 📦 Installation

### Step 1: Clone/Download the Project

```bash
cd gmail-to-sheets
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### 1. Enable Gmail and Sheets APIs

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Navigate to **APIs & Services > Library**
4. Search and enable:
   - **Gmail API**
   - **Google Sheets API**

### 2. Create OAuth 2.0 Credentials

1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials > OAuth client ID**
3. Choose **Desktop app** as application type
4. Download the JSON file
5. Rename it to `credentials.json`
6. Move it to `gmail-to-sheets/credentials/` folder

**⚠️ CRITICAL**: Never commit `credentials.json` to version control!

### 2a. First Authentication - OAuth Consent Screen

When you run the script for the first time, you'll see a Google OAuth consent screen:

```
┌─────────────────────────────────────────────────────────┐
│  Sign in with Google                                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Gmail to Google Sheets Automation                      │
│  wants access to your Google Account                    │
│                                                         │
│  [Google Icon]                                          │
│                                                         │
│  "Gmail to Google Sheets Automation" would like to:     │
│                                                         │
│  ☑ See, edit, create, and delete all your Google       │
│    Sheets spreadsheets                                  │
│                                                         │
│  ☑ Read, compose, send, and permanently delete all     │
│    your email from Gmail                                │
│                                                         │
│  Your email may be blurred                             │
│                                                         │
│  ┌──────────────────────────────────────────┐          │
│  │ [Cancel]  [Allow/Continue]               │          │
│  └──────────────────────────────────────────┘          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**What permissions are requested:**
- ✅ Read your Gmail messages (including unread emails)
- ✅ Modify your Gmail labels (to mark emails as read)
- ✅ Create, read, and modify Google Sheets

**Important Notes:**
- You must click **"Allow"** or **"Continue"** to proceed
- Google will generate a `token.json` file automatically
- This token is saved locally in the `credentials/` folder
- The token auto-refreshes, so you won't need to authenticate again
- Token expires after 6 months of non-use (requires re-authentication)
- Your email address may appear blurred for privacy

#### 🔄 How to Force the Consent Screen (If You Need to See It Again)

**Your system is currently using saved credentials.** If you want to see the OAuth consent screen again:

**Step 1: Delete Old OAuth Token**

Go to your project folder and delete the token file:

```bash
# Windows
del credentials\token.json

# macOS/Linux
rm credentials/token.json
```

**Why?**
- Google shows consent screen **only on first login**
- Deleting `token.json` forces re-authentication
- System will prompt you for permissions again

**Step 2: Run Your Script**

```bash
python src/main.py
```

**What happens:**
- Script detects missing token
- Opens browser automatically
- Shows OAuth consent screen
- After clicking "Allow", generates new `token.json`
- Script continues execution normally

### 3. Create Google Sheet

1. Create a new Google Sheet
2. Copy the **Spreadsheet ID** from the URL:
   ```
   https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit
   ```
3. Open `config.py` and update:
   ```python
   SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID_HERE'
   ```

### 4. Customize Configuration (Optional)

Edit `config.py` to customize:
- **GMAIL_QUERY**: Change email filters (e.g., add subject filters)
- **MAX_EMAILS_PER_RUN**: Limit emails processed per execution
- **SHEET_NAME**: Change target sheet tab name

---

## 🚀 Usage

### First Run

```bash
cd gmail-to-sheets
python src/main.py
```

**What happens:**
1. Browser opens for OAuth authentication
2. Grant permissions to Gmail and Sheets
3. `token.json` is created automatically
4. Script fetches unread emails
5. Emails are appended to Google Sheets
6. Emails are marked as read
7. State file is updated

### Subsequent Runs

```bash
python src/main.py
```

No browser authentication needed (uses saved `token.json`).

### Safe Re-runs

You can run the script multiple times safely:
- Already processed emails are **skipped**
- Only new unread emails are processed
- No duplicates in Google Sheets

---

## 🔄 How It Works

### Execution Flow

```
1. Initialize State Manager
   └─ Load processed_ids.json (contains processed email IDs)

2. Authenticate with Gmail
   └─ Use token.json or initiate OAuth flow

3. Authenticate with Google Sheets
   └─ Reuse token.json from Gmail auth

4. Verify Sheet Access
   └─ Check if spreadsheet exists and is accessible

5. Create Header Row (if needed)
   └─ Add: From | Subject | Date | Content

6. Fetch Unread Emails
   └─ Query: is:unread in:inbox

7. Parse Emails
   └─ Extract: From, Subject, Date, Plain Text Body

8. Filter New Emails
   └─ Skip emails already in processed_ids

9. Append to Google Sheets
   └─ Batch insert new email rows (Message ID | From | Subject | Date | Content)

10. Mark as Read in Gmail
    └─ Remove UNREAD label from processed emails

11. Update State File
    └─ Save new message IDs to processed_ids.json

12. Log Summary
    └─ Report: fetched, new, processed, total lifetime
```

---

## 🧹 HTML → Plain Text Conversion (Mandatory)

- Most emails are HTML; storing raw HTML would violate the assignment. We must store **plain text only**.
- Parser logic: prefer `text/plain` MIME parts; if absent, convert `text/html` to plain text using BeautifulSoup (strip tags, scripts, styles; keep readable text).
- Plain text means characters, spaces, and line breaks only — no tags, fonts, or styling. We truncate very long bodies to fit Sheets limits.

---

## 🛡️ Duplicate Prevention Strategy

### Why It's Needed

Without duplicate prevention:
- Re-running the script would reprocess all unread emails
- Same emails would appear multiple times in Google Sheets
- Data integrity is compromised

### Implementation: Message ID Tracking

We use **Gmail Message IDs** which are:
- Unique for each email
- Persistent (never change)
- Returned by Gmail API

### How It Works

1. **Sheet Column**: Column A stores Message IDs already logged.
2. **State File**: `processed_ids.json` stores all processed Message IDs locally.
3. **Before Processing**: We check both sheet IDs and state file.
4. **Skip Duplicates**: If Message ID exists, we skip processing/appending.
5. **After Processing**: Add new Message IDs to sheet (new rows) and to state file.
6. **Persist State**: Save to disk after each run → idempotent reruns.

### Example State File

```json
{
  "processed_message_ids": [
    "18d3e5f2a8b9c0d1",
    "18d3e6f3b9c1d2e3",
    "18d3e7f4c0d2e4f5"
  ],
  "last_updated": "2026-01-13 10:30:45"
}
```

---

## 💾 State Persistence

### Why Message ID Tracking Over HistoryId?

We chose **message ID tracking** over Gmail's `historyId` for these reasons:

#### Message ID Approach (Chosen)
✅ **Simple**: Easy to understand and implement  
✅ **Reliable**: Message IDs never change  
✅ **Flexible**: Works even if emails are re-labeled  
✅ **Transparent**: Can manually inspect processed IDs  
✅ **No API Complexity**: No need to track history changes  

#### HistoryId Approach (Not Chosen)
❌ **Complex**: Requires understanding Gmail's history mechanism  
❌ **Fragile**: History can reset or become invalid  
❌ **API Overhead**: Need to fetch and compare history changes  
❌ **Edge Cases**: Harder to handle corner cases  

### State File Location

`processed_ids.json` is stored in the project root directory.

**Important**: 
- Don't delete this file (you'll reprocess all emails)
- It's excluded from git via `.gitignore`
- Grows over time (one ID per processed email)

---

## What Happens If You Run the Script Twice?

- First run: pulls INBOX+UNREAD, logs rows with Message ID, marks them read, stores IDs in sheet + state.
- Second run (immediately): UNREAD labels removed, so API returns 0; even if an email reappeared, Message ID dedupe against sheet + state prevents duplicates → 0 new rows.

---

## Proof of Execution (What to Show)

- Console log: shows counts for fetched, new, inserted, and total processed; also shows marking emails as read.
- Google Sheet: Column A contains Message IDs; rows match the log counts; no duplicates after reruns.
- Gmail UI: Inbox unread count drops because UNREAD label is removed via API; rerun should log “No unread emails found.”

---

## 🔐 OAuth Flow

### First-Time Authentication

1. Script checks for `token.json`
2. Not found → Opens browser
3. User logs into Google account
4. User grants permissions:
   - Read Gmail messages
   - Modify Gmail labels (mark as read)
   - Edit Google Sheets
5. Google redirects to local server
6. Script receives authorization code
7. Exchanges code for access/refresh tokens
8. Saves tokens to `credentials/token.json`

### Subsequent Authentications

1. Script loads `token.json`
2. Checks if token is valid
3. If expired → Refreshes using refresh token
4. If refresh fails → Re-initiates OAuth flow

### Token Security

- Tokens are stored locally in `credentials/`
- **Never commit `token.json` to git**
- Tokens have read/write access to your Gmail and Sheets
- If compromised, revoke access in [Google Account Settings](https://myaccount.google.com/permissions)

---

## 🧩 Challenges & Solutions

### Challenge 1: HTML Email Bodies

**Problem**: Many emails are HTML-formatted, not plain text.

**Solution**: 
- Use BeautifulSoup4 to parse HTML
- Extract text content
- Remove scripts, styles, and formatting
- Fallback to raw HTML if parsing fails

### Challenge 2: Multipart MIME Messages

**Problem**: Emails can have multiple parts (text, HTML, attachments).

**Solution**:
- Parse MIME structure recursively
- Prioritize `text/plain` over `text/html`
- Handle nested multipart structures

### Challenge 3: Base64 Decoding

**Problem**: Gmail API returns body content in URL-safe base64.

**Solution**:
- Use `base64.urlsafe_b64decode()`
- Handle decode errors gracefully
- Support UTF-8 and other encodings

### Challenge 4: API Rate Limits

**Problem**: Gmail API has quota limits (batch size, requests per day).

**Solution**:
- Limit emails per run (`MAX_EMAILS_PER_RUN = 50`)
- Batch operations where possible
- Implement error handling for quota errors
- Add retry logic for transient failures

### Challenge 5: Large Email Content

**Problem**: Very long emails exceed Google Sheets cell limit (50,000 chars).

**Solution**:
- Truncate content to 40,000 characters
- Add "[Content truncated]" message
- Log truncation events

### Challenge 6: Concurrent Runs

**Problem**: Running script multiple times simultaneously could cause race conditions.

**Solution**:
- State file locking (future enhancement)
- Current: Designed for sequential runs
- Recommendation: Use task scheduler for automation

---

## ⚠️ Limitations

1. **Email Volume**: 
   - Processes max 50 emails per run (configurable)
   - For large inboxes, may need multiple runs

2. **Attachments**:
   - Not downloaded or processed
   - Only email metadata and body text

3. **Concurrent Execution**:
   - Not designed for parallel runs
   - State file could become inconsistent

4. **API Quotas**:
   - Subject to Gmail API daily quotas
   - Default: 1 billion quota units/day (generous)

5. **Sheet Size**:
   - Google Sheets supports up to 10 million cells
   - Long emails consume more cells

6. **OAuth Token Expiry**:
   - Refresh tokens can expire if not used for 6 months
   - Requires re-authentication

7. **No Real-time Sync**:
   - Must manually run script
   - Not a continuous sync service

8. **Single User**:
   - OAuth credentials are user-specific
   - Each user needs their own setup

---

## 🔒 Security Considerations

### Security Rules (Mandatory)

- Do **NOT** commit API keys, OAuth tokens, or `credentials.json`.
- Repositories committing these secrets are rejected automatically; keep them local only.

### Critical Files (NEVER COMMIT)

- `credentials/credentials.json` → OAuth client secrets
- `credentials/token.json` → User access tokens
- `processed_ids.json` → Could reveal email patterns

### .gitignore Rules

All sensitive files are excluded via `.gitignore`:

```
credentials/credentials.json
credentials/token.json
token.json
processed_ids.json
```

### Best Practices

1. **Credentials**: 
   - Store in secure location
   - Don't share or email
   - Regenerate if compromised

2. **Tokens**:
   - Auto-generated, don't share
   - Revoke access if suspicious activity
   - Refresh automatically

3. **API Scopes**:
   - Use minimum required scopes
   - Review granted permissions regularly

4. **Spreadsheet Access**:
   - Limit sheet sharing
   - Use private or restricted sheets

---

## 🐛 Troubleshooting

### "Credentials file not found"

**Cause**: `credentials.json` missing or in wrong location.

**Fix**:
1. Download from Google Cloud Console
2. Place in `credentials/` folder
3. Ensure filename is exactly `credentials.json`

### "Spreadsheet not found"

**Cause**: Invalid `SPREADSHEET_ID` in `config.py`.

**Fix**:
1. Open your Google Sheet
2. Copy ID from URL: `https://docs.google.com/spreadsheets/d/{ID}/edit`
3. Update `config.py`

### "Permission denied" or "Access not configured"

**Cause**: Gmail or Sheets API not enabled.

**Fix**:
1. Go to Google Cloud Console
2. Enable Gmail API and Google Sheets API
3. Wait 1-2 minutes for propagation

### "Token has been expired or revoked"

**Cause**: OAuth token expired or manually revoked.

**Fix**:
1. Delete `credentials/token.json`
2. Run script again
3. Complete OAuth flow in browser

### "No unread emails found" but emails exist

**Cause**: Emails might not be in Inbox or are already marked as read.

**Fix**:
1. Check `config.py` → `GMAIL_QUERY`
2. Ensure emails match query: `is:unread in:inbox`
3. Test with a test email

### Script hangs during execution

**Cause**: Network issues or API timeout.

**Fix**:
1. Check internet connection
2. Restart script
3. Check Google API status page

---

## 🚀 Future Enhancements

### Potential Features

1. **Filtering by Subject**: Add keyword filters in config
2. **Attachment Download**: Save attachments to local folder or cloud storage
3. **Multiple Sheets**: Support for different categories (work, personal, etc.)
4. **Webhook Integration**: Real-time email processing with Cloud Functions
5. **Email Summarization**: AI-powered email summaries using OpenAI/GPT
6. **Search in Sheets**: Full-text search capability
7. **Scheduler Integration**: Automatic runs via cron/Task Scheduler
8. **Email Reply Tracking**: Track which emails have been replied to
9. **Analytics Dashboard**: Visualize email trends
10. **Multi-user Support**: Service account for team access

### Suggested Scheduler Setup

**Windows (Task Scheduler)**:
```powershell
schtasks /create /tn "Gmail to Sheets" /tr "C:\path\to\venv\Scripts\python.exe C:\path\to\src\main.py" /sc hourly
```

**macOS/Linux (cron)**:
```bash
0 * * * * /path/to/venv/bin/python /path/to/src/main.py >> /path/to/logs/cron.log 2>&1
```

---

## 📞 Support

### Getting Help

1. **Check Logs**: Review console output for error messages
2. **Verify Setup**: Ensure all prerequisites are met
3. **Test APIs**: Verify APIs are enabled in Google Cloud Console
4. **Inspect State**: Check `processed_ids.json` for consistency

### Common Issues

- OAuth errors → Re-authenticate
- API quota → Wait 24 hours or request increase
- Parse errors → Check email format

---

## 📄 License

This project is provided as-is for educational and production use. Modify as needed for your specific requirements.

---

## 🎯 Summary

This Gmail to Google Sheets automation provides a robust, production-ready solution for:
- ✅ Real-time email fetching
- ✅ Automatic Google Sheets integration
- ✅ Duplicate prevention through state management
- ✅ Secure OAuth 2.0 authentication
- ✅ Clean, maintainable codebase
- ✅ Comprehensive error handling
- ✅ Safe re-execution

**Ready to use. Ready for production. Ready for customization.**

---

*Built with Python 3 | Gmail API | Google Sheets API | OAuth 2.0*
