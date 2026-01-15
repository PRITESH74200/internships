# CREDENTIALS FOLDER

## ⚠️ IMPORTANT INSTRUCTIONS

This folder should contain your OAuth 2.0 credentials:

### Required Files:

1. **credentials.json** (YOU MUST ADD THIS)
   - Download from Google Cloud Console
   - Do NOT commit to version control
   - Contains OAuth client ID and secret

2. **token.json** (AUTO-GENERATED)
   - Created automatically on first run
   - Stores your access and refresh tokens
   - Do NOT commit to version control

---

## How to Get credentials.json

1. Go to: https://console.cloud.google.com/
2. Create or select a project
3. Enable Gmail API and Google Sheets API
4. Go to "APIs & Services" > "Credentials"
5. Create "OAuth client ID" (Desktop app)
6. Download the JSON file
7. Rename to `credentials.json`
8. Place in THIS folder

---

## Security Notice

🔒 **NEVER commit these files to Git!**

Both files are already excluded in `.gitignore`:
```
credentials/credentials.json
credentials/token.json
```

If you accidentally commit them:
1. Remove from git history immediately
2. Revoke access in Google Cloud Console
3. Generate new credentials

---

## Folder Structure

```
credentials/
├── credentials.json    ← YOU ADD THIS (from Google Cloud)
├── token.json          ← AUTO-GENERATED (by script)
└── README.txt          ← This file
```

---

**See SETUP.md for detailed setup instructions.**
