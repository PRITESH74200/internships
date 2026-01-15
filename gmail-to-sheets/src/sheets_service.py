"""
Google Sheets Service Module
Handles Google Sheets API authentication and data operations.
"""

import os
import logging
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logger = logging.getLogger(__name__)


class SheetsService:
    """
    Google Sheets Service class for authentication and sheet operations.
    """
    
    def __init__(self):
        """Initialize Sheets service with OAuth authentication."""
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """
        Authenticate with Google Sheets API using OAuth 2.0.
        
        Reuses existing credentials from Gmail authentication (same token.json).
        If credentials don't exist, initiates OAuth flow.
        """
        creds = None
        
        # Check if token file exists
        if os.path.exists(config.TOKEN_FILE):
            logger.info("Loading existing credentials from token.json")
            creds = Credentials.from_authorized_user_file(config.TOKEN_FILE, config.SCOPES)
        
        # If credentials don't exist or are invalid, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired credentials")
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.warning(f"Failed to refresh credentials: {e}")
                    creds = None
            
            if not creds:
                # Credentials file must exist
                if not os.path.exists(config.CREDENTIALS_FILE):
                    raise FileNotFoundError(
                        f"Credentials file not found at: {config.CREDENTIALS_FILE}\n"
                        f"Please download credentials.json from Google Cloud Console."
                    )
                
                logger.info("Starting OAuth 2.0 flow")
                flow = InstalledAppFlow.from_client_secrets_file(
                    config.CREDENTIALS_FILE, 
                    config.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            logger.info("Saving credentials to token.json")
            with open(config.TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        
        # Build Sheets API service
        self.service = build('sheets', 'v4', credentials=creds)
        logger.info("Google Sheets API service initialized successfully")
    
    def get_existing_message_ids(self) -> set:
        """
        Fetch all Gmail message IDs already present in the spreadsheet.

        Returns:
            Set of message IDs (column A, skipping header if present)
        """
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=config.SPREADSHEET_ID,
                range=f'{config.SHEET_NAME}!A2:A'
            ).execute()

            values = result.get('values', [])
            # Flatten first column values into a set, ignore empty rows
            existing_ids = {row[0] for row in values if row and row[0]}
            logger.info(f"Fetched {len(existing_ids)} existing message IDs from sheet for dedupe")
            return existing_ids
        except HttpError as error:
            logger.error(f"Error fetching existing message IDs: {error}")
            return set()
    
    def append_emails(self, emails: List[Dict[str, str]]) -> bool:
        """
        Insert email data at the top of Google Sheets (row 2, right after header).
        
        Args:
            emails: List of email dictionaries with keys: message_id, from, subject, date, content
        
        Returns:
            True if successful, False otherwise
        """
        if not emails:
            logger.info("No emails to append")
            return True
        
        try:
            # Prepare rows for insertion
            rows = []
            for email in emails:
                row = [
                    email.get('message_id', ''),
                    email.get('from', ''),
                    email.get('subject', ''),
                    email.get('date', ''),
                    email.get('content', '')
                ]
                rows.append(row)
            
            # First, insert empty rows at position 2 to make space
            insert_request = {
                'requests': [{
                    'insertDimension': {
                        'range': {
                            'sheetId': 0,
                            'dimension': 'ROWS',
                            'startIndex': 1,  # Row 2 (0-indexed)
                            'endIndex': 1 + len(rows)  # Insert len(rows) rows
                        },
                        'inheritFromBefore': False
                    }
                }]
            }
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=config.SPREADSHEET_ID,
                body=insert_request
            ).execute()
            
            # Then update the newly inserted rows with email data
            body = {
                'values': rows
            }
            result = self.service.spreadsheets().values().update(
                spreadsheetId=config.SPREADSHEET_ID,
                range=f'{config.SHEET_NAME}!A2:E{1 + len(rows)}',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            rows_updated = len(rows)
            
            logger.info(f"Successfully inserted {rows_updated} row(s) at top of Google Sheets")
            return True
        
        except HttpError as error:
            logger.error(f"An error occurred while inserting to Sheets: {error}")
            if 'Requested entity was not found' in str(error):
                logger.error(
                    f"Spreadsheet not found. Please check SPREADSHEET_ID in config.py: "
                    f"{config.SPREADSHEET_ID}"
                )
            return False
        except Exception as e:
            logger.error(f"Unexpected error inserting to Sheets: {e}")
            return False
    
    def create_header_row(self) -> bool:
        """
        Create header row in the spreadsheet if it doesn't exist.
        
        Headers: From | Subject | Date | Content
        
        Returns:
            True if successful or headers already exist
        """
        try:
            # Check if first row exists
            result = self.service.spreadsheets().values().get(
                spreadsheetId=config.SPREADSHEET_ID,
                range=f'{config.SHEET_NAME}!A1:E1'
            ).execute()
            
            values = result.get('values', [])
            
            # If first row is empty, add headers
            if not values:
                logger.info("Creating header row in Google Sheets")
                headers = [['Message ID', 'From', 'Subject', 'Date', 'Content']]
                body = {'values': headers}
                
                self.service.spreadsheets().values().update(
                    spreadsheetId=config.SPREADSHEET_ID,
                    range=f'{config.SHEET_NAME}!A1:E1',
                    valueInputOption='RAW',
                    body=body
                ).execute()
                
                logger.info("Header row created successfully")
            else:
                logger.info("Header row already exists")
            
            return True
        
        except HttpError as error:
            logger.error(f"Error creating header row: {error}")
            return False
    
    def get_sheet_info(self) -> Optional[Dict]:
        """
        Get spreadsheet metadata.
        
        Returns:
            Dictionary with sheet info or None if error
        """
        try:
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=config.SPREADSHEET_ID
            ).execute()
            
            properties = spreadsheet.get('properties', {})
            return {
                'title': properties.get('title', 'Unknown'),
                'sheets': len(spreadsheet.get('sheets', []))
            }
        except HttpError as error:
            logger.error(f"Error getting sheet info: {error}")
            return None
    
    def verify_sheet_access(self) -> bool:
        """
        Verify that the spreadsheet exists and is accessible.
        
        Returns:
            True if accessible, False otherwise
        """
        try:
            info = self.get_sheet_info()
            if info:
                logger.info(f"Successfully accessed spreadsheet: {info.get('title')}")
                return True
            return False
        except Exception as e:
            logger.error(f"Cannot access spreadsheet: {e}")
            return False
