# Quick Start Guide

## Setup in 5 Minutes

### 1. Install Dependencies
```bash
cd gmail-to-sheets
pip install -r requirements.txt
```

### 2. Get Google Cloud Credentials

#### A. Create Google Cloud Project
1. Visit: https://console.cloud.google.com/
2. Click "New Project"
3. Name it "Gmail to Sheets"
4. Click "Create"

#### B. Enable APIs
1. Go to "APIs & Services" > "Library"
2. Search "Gmail API" → Click → Enable
3. Search "Google Sheets API" → Click → Enable

#### C. Create OAuth Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Configure Consent Screen"
   - Choose "External"
   - App name: "Gmail to Sheets"
   - User support email: (your email)
   - Developer email: (your email)
   - Click "Save and Continue" (skip optional fields)
3. Click "Credentials" tab
4. Click "Create Credentials" > "OAuth client ID"
5. Application type: "Desktop app"
6. Name: "Gmail to Sheets Desktop"
7. Click "Create"
8. Click "Download JSON"
9. Save as `credentials.json` in `gmail-to-sheets/credentials/` folder

### 3. Create Google Sheet
1. Go to: https://docs.google.com/spreadsheets/
2. Click "+ Blank" to create new sheet
3. Copy the ID from URL:
   ```
   https://docs.google.com/spreadsheets/d/[THIS_IS_THE_ID]/edit
   ```

### 4. Configure the Project
1. Open `config.py`
2. Replace `YOUR_SPREADSHEET_ID_HERE` with your actual ID:
   ```python
   SPREADSHEET_ID = '1aB2cD3eF4gH5iJ6kL7mN8oP9qR0sT1uV2wX3yZ'
   ```

### 5. Run the Script
```bash
python src/main.py
```

**First run will:**
- Open browser for authentication
- Ask you to login to Google
- Request permissions for Gmail and Sheets
- Save token for future runs
- Fetch unread emails
- Append to Google Sheets

### 6. Verify Results
1. Open your Google Sheet
2. See emails in columns: From | Subject | Date | Content
3. Check Gmail - emails should be marked as read

---

## Testing with Sample Email

Before running on your real inbox, test with a sample email:

1. Send yourself a test email with subject "Test Email for Automation"
2. Keep it unread
3. Run the script: `python src/main.py`
4. Verify it appears in Google Sheets
5. Verify it's marked as read in Gmail
6. Run script again - verify it's NOT duplicated

---

## Common First-Run Issues

### "credentials.json not found"
- **Fix**: Place `credentials.json` in `credentials/` folder

### "SPREADSHEET_ID not configured"
- **Fix**: Update `config.py` with your actual Sheet ID

### Browser doesn't open for OAuth
- **Fix**: Check firewall, try a different browser
- **Alternative**: Copy URL from console and paste in browser manually

### "Access not configured"
- **Fix**: Wait 2-3 minutes after enabling APIs
- Try again

---

## Scheduling Automatic Runs

### Windows Task Scheduler
```powershell
# Run every hour
schtasks /create /tn "Gmail Sync" /tr "C:\path\to\venv\Scripts\python.exe C:\path\to\gmail-to-sheets\src\main.py" /sc hourly
```

### macOS/Linux Cron
```bash
# Edit crontab
crontab -e

# Add line (runs every hour)
0 * * * * /path/to/venv/bin/python /path/to/gmail-to-sheets/src/main.py >> /path/to/logs/gmail-sync.log 2>&1
```

---

## Customization Examples

### Filter by Subject
Edit `config.py`:
```python
GMAIL_QUERY = 'is:unread in:inbox subject:invoice'
```

### Change Max Emails per Run
Edit `config.py`:
```python
MAX_EMAILS_PER_RUN = 100
```

### Use Different Sheet Tab
Edit `config.py`:
```python
SHEET_NAME = 'Emails'  # Instead of Sheet1
```

---

## Need Help?

1. Check [README.md](README.md) for detailed documentation
2. Review logs in console output
3. Verify all prerequisites in "Prerequisites" section
4. Test OAuth credentials in Google Cloud Console

---

**You're all set! The automation is ready to use. 🚀**
