# Fix OAuth Error 403: Access Blocked

## Problem
Your app shows: "Access blocked: Gmail to Sheets has not completed the Google verification process"

This happens because your OAuth consent screen is in **Testing mode** and your email (`priteshbalgundi873@gmail.com`) is not added as a test user.

---

## Solution: Add Test User (5 minutes)

### Step 1: Go to Google Cloud Console
1. Visit: https://console.cloud.google.com/
2. Select your "Gmail to Sheets" project from the dropdown at the top

### Step 2: Navigate to OAuth Consent Screen
1. In the left menu, click **"APIs & Services"**
2. Click **"OAuth consent screen"**

### Step 3: Add Test Users
1. Scroll down to **"Test users"** section
2. Click **"+ ADD USERS"** button
3. Enter your email: `priteshbalgundi873@gmail.com`
4. Click **"SAVE"**

### Step 4: Clear Previous Authentication
Delete the token file so you can re-authenticate:
```powershell
# Run this in your terminal
Remove-Item "c:\Users\Pritesh\OneDrive\Desktop\internships\gmail-to-sheets\credentials\token.json" -ErrorAction SilentlyContinue
```

### Step 5: Run the Application Again
```powershell
cd c:\Users\Pritesh\OneDrive\Desktop\internships\gmail-to-sheets
python src/main.py
```

The OAuth flow should now work and allow you to sign in!

---

## Alternative: Publish the App (Not Recommended for Testing)

If you want anyone to use your app without adding them as test users, you need to:
1. Go to OAuth consent screen
2. Click **"PUBLISH APP"**
3. Submit for Google verification (takes weeks and requires security assessment)

**For personal/testing use, just add yourself as a test user instead!**

---

## Verification Checklist

After adding test user, verify:
- ✅ Email `priteshbalgundi873@gmail.com` appears in test users list
- ✅ Deleted `token.json` file
- ✅ Run `python src/main.py`
- ✅ Browser opens for OAuth
- ✅ Can sign in without "Access blocked" error
- ✅ Emails appear in Google Sheets

---

## Still Having Issues?

### Error: "This app is blocked"
- Make sure you added the EXACT email address you're signing in with
- Wait 1-2 minutes after adding test user
- Try incognito/private browser window

### Error: "Invalid client"
- Your `credentials.json` might be from wrong project
- Re-download credentials from the correct Google Cloud project

### Can't find OAuth consent screen
- Make sure you're in the correct project
- Check that Gmail API and Sheets API are enabled

---

## Quick Visual Guide

1. **Google Cloud Console** → Select Project
2. **APIs & Services** → OAuth consent screen
3. Scroll to **Test users** section
4. Click **+ ADD USERS**
5. Enter `priteshbalgundi873@gmail.com`
6. Click **SAVE**
7. Delete `token.json` in credentials folder
8. Run `python src/main.py`

✅ **Done!** You should now be able to authenticate.
