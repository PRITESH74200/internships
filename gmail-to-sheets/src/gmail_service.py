"""
Gmail Service Module
Handles Gmail API authentication, fetching unread emails, and marking them as read.
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


class GmailService:
    """
    Gmail Service class for authentication and email operations.
    """
    
    def __init__(self):
        """Initialize Gmail service with OAuth authentication."""
        self.service = None
        self.has_modify_permission = False
        self.authenticate()
    
    def authenticate(self):
        """
        Authenticate with Gmail API using OAuth 2.0.
        
        Creates or reuses token.json for persistent authentication.
        If token.json doesn't exist or is invalid, initiates OAuth flow.
        """
        creds = None
        
        # Check if token file exists (stores user's access and refresh tokens)
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
                # Run local server for OAuth callback
                # Handle partial scope grants (when gmail.modify is not approved)
                try:
                    creds = flow.run_local_server(port=0)
                except Warning as w:
                    # Scope mismatch warning - Google didn't grant all scopes
                    # This is OK, we'll work with what we got
                    logger.warning(f"Not all scopes were granted: {w}")
                    creds = flow.credentials
            
            # Save credentials for next run
            logger.info("Saving credentials to token.json")
            with open(config.TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        
        # Check which scopes were actually granted
        granted_scopes = creds.scopes if hasattr(creds, 'scopes') and creds.scopes else []
        self.has_modify_permission = 'https://www.googleapis.com/auth/gmail.modify' in granted_scopes
        
        if not self.has_modify_permission:
            logger.warning("gmail.modify scope not granted - emails will NOT be marked as read")
            logger.warning("To enable marking emails as read, add 'gmail.modify' to sensitive scopes in OAuth consent screen")
        
        # Build Gmail API service
        self.service = build('gmail', 'v1', credentials=creds)
        logger.info(f"Gmail API service initialized successfully (modify permission: {self.has_modify_permission})")
    
    def fetch_unread_emails(self, max_results: int = None) -> List[Dict]:
        """
        Fetch unread emails from Gmail inbox.
        
        Args:
            max_results: Maximum number of emails to fetch (default from config)
        
        Returns:
            List of email message dictionaries with full metadata
        """
        if max_results is None:
            max_results = config.MAX_EMAILS_PER_RUN
        
        try:
            logger.info(f"Fetching unread emails with query: {config.GMAIL_QUERY}")
            
            # List messages matching the query
            results = self.service.users().messages().list(
                userId='me',
                q=config.GMAIL_QUERY,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                logger.info("No unread emails found")
                return []
            
            logger.info(f"Found {len(messages)} unread email(s)")
            
            # Fetch full message details for each email
            full_messages = []
            for msg in messages:
                try:
                    message = self.service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='full'  # Get full message including body
                    ).execute()
                    full_messages.append(message)
                except HttpError as error:
                    logger.error(f"Error fetching message {msg['id']}: {error}")
                    continue
            
            logger.info(f"Successfully fetched {len(full_messages)} complete email(s)")
            return full_messages
        
        except HttpError as error:
            logger.error(f"An error occurred while fetching emails: {error}")
            return []
    
    def mark_as_read(self, message_id: str) -> bool:
        """
        Mark an email as read by removing the UNREAD label.
        Only works if gmail.modify permission was granted during OAuth.
        
        Args:
            message_id: Gmail message ID
        
        Returns:
            True if successful, False otherwise
        """
        if not self.has_modify_permission:
            logger.debug(f"Skipping mark as read for {message_id} - no modify permission")
            return False
            
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            logger.info(f"Marked email {message_id} as read")
            return True
        
        except HttpError as error:
            logger.error(f"Error marking email {message_id} as read: {error}")
            return False
    
    def mark_multiple_as_read(self, message_ids: List[str]) -> int:
        """
        Mark multiple emails as read.
        
        Args:
            message_ids: List of Gmail message IDs
        
        Returns:
            Number of emails successfully marked as read
        """
        success_count = 0
        for message_id in message_ids:
            if self.mark_as_read(message_id):
                success_count += 1
        
        logger.info(f"Marked {success_count}/{len(message_ids)} emails as read")
        return success_count
    
    def get_user_email(self) -> Optional[str]:
        """
        Get the authenticated user's email address.
        
        Returns:
            User's email address or None if error
        """
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return profile.get('emailAddress')
        except HttpError as error:
            logger.error(f"Error getting user profile: {error}")
            return None
