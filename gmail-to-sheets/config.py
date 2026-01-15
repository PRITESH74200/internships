"""
Configuration file for Gmail to Google Sheets automation.
Contains API scopes, file paths, and spreadsheet settings.

WARNING: Never commit credentials.json or token.json to version control!
"""

import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Credentials and token paths
CREDENTIALS_DIR = os.path.join(BASE_DIR, 'credentials')
CREDENTIALS_FILE = os.path.join(CREDENTIALS_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(CREDENTIALS_DIR, 'token.json')

# State persistence file (stores processed email IDs)
STATE_FILE = os.path.join(BASE_DIR, 'processed_ids.json')

# Gmail API Scopes
# - gmail.readonly: Read emails
# - gmail.modify: Mark emails as read
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

# Google Sheets API Scopes
SHEETS_SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets'
]

# Combined scopes for unified OAuth flow
SCOPES = GMAIL_SCOPES + SHEETS_SCOPES

# ========================================
# GOOGLE SHEETS CONFIGURATION
# ========================================
# TODO: Replace with your actual Google Sheets ID
# Find this in the URL: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit
SPREADSHEET_ID = '1ITYGr0T8txyMw_S8qmpSBCfy-4zjrma5JZQFUzgpQF8'

# Sheet name (tab) where emails will be appended
SHEET_NAME = 'Sheet1'

# Sheet range (A1 notation)
# Columns: Message ID | From | Subject | Date | Content
SHEET_RANGE = f'{SHEET_NAME}!A:E'

# ========================================
# GMAIL QUERY CONFIGURATION
# ========================================
# Gmail search query to fetch emails
# Current: Unread emails in Inbox only (matches Gmail UI when UNREAD is removed via API)
# Customize to add filters (e.g., 'is:unread label:INBOX subject:invoice')
GMAIL_QUERY = 'is:unread label:INBOX'

# Maximum number of emails to process per run (safety limit)
MAX_EMAILS_PER_RUN = 50

# ========================================
# LOGGING CONFIGURATION
# ========================================
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
