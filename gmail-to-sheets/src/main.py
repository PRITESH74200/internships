"""
Main orchestration script for Gmail to Google Sheets automation.

This script:
1. Authenticates with Gmail and Google Sheets APIs
2. Fetches unread emails from Gmail inbox
3. Parses email content
4. Filters out already processed emails
5. Appends new emails to Google Sheets
6. Marks processed emails as read
7. Updates state file to prevent reprocessing
"""

import os
import sys
import json
import logging
from typing import List, Dict, Set

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from src.gmail_service import GmailService
from src.sheets_service import SheetsService
from src.email_parser import EmailParser

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


class StateManager:
    """
    Manages state persistence to prevent reprocessing of emails.
    
    Uses a JSON file to store processed message IDs.
    """
    
    def __init__(self, state_file: str = config.STATE_FILE):
        """
        Initialize state manager.
        
        Args:
            state_file: Path to JSON file storing processed message IDs
        """
        self.state_file = state_file
        self.processed_ids = self._load_state()
    
    def _load_state(self) -> Set[str]:
        """
        Load processed message IDs from state file.
        
        Returns:
            Set of processed message IDs
        """
        if not os.path.exists(self.state_file):
            logger.info("State file not found. Creating new state.")
            return set()
        
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                processed_ids = set(data.get('processed_message_ids', []))
                logger.info(f"Loaded {len(processed_ids)} processed message IDs from state")
                return processed_ids
        except Exception as e:
            logger.error(f"Error loading state file: {e}")
            return set()
    
    def save_state(self) -> bool:
        """
        Save current state to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                'processed_message_ids': list(self.processed_ids),
                'last_updated': logging.Formatter().formatTime(
                    logging.LogRecord('', 0, '', 0, '', (), None)
                )
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"State saved: {len(self.processed_ids)} message IDs")
            return True
        except Exception as e:
            logger.error(f"Error saving state file: {e}")
            return False
    
    def is_processed(self, message_id: str) -> bool:
        """
        Check if a message has been processed.
        
        Args:
            message_id: Gmail message ID
        
        Returns:
            True if already processed, False otherwise
        """
        return message_id in self.processed_ids
    
    def mark_processed(self, message_id: str):
        """
        Mark a message as processed.
        
        Args:
            message_id: Gmail message ID
        """
        self.processed_ids.add(message_id)
    
    def mark_batch_processed(self, message_ids: List[str]):
        """
        Mark multiple messages as processed.
        
        Args:
            message_ids: List of Gmail message IDs
        """
        self.processed_ids.update(message_ids)


def filter_new_emails(emails: List[Dict], state_manager: StateManager, sheet_ids: Set[str]) -> List[Dict]:
    """
    Filter out already processed emails.
    
    Args:
        emails: List of parsed email dictionaries
        state_manager: StateManager instance
    
    Returns:
        List of new (unprocessed) emails
    """
    new_emails = []
    skipped = 0
    
    for email in emails:
        message_id = email.get('message_id')
        if not message_id:
            logger.warning("Email missing message_id, skipping")
            continue

        if state_manager.is_processed(message_id) or message_id in sheet_ids:
            skipped += 1
            logger.debug(f"Skipping already processed email: {message_id}")
        else:
            new_emails.append(email)
    
    logger.info(f"Filtered emails: {len(new_emails)} new, {skipped} already processed")
    return new_emails


def main():
    """
    Main execution flow.
    """
    logger.info("=" * 60)
    logger.info("Gmail to Google Sheets Automation - Starting")
    logger.info("=" * 60)
    
    try:
        # Initialize state manager
        logger.info("Step 1: Initializing state manager")
        state_manager = StateManager()
        
        # Initialize Gmail service
        logger.info("Step 2: Authenticating with Gmail API")
        gmail = GmailService()
        
        user_email = gmail.get_user_email()
        if user_email:
            logger.info(f"Authenticated as: {user_email}")
        
        # Initialize Sheets service
        logger.info("Step 3: Authenticating with Google Sheets API")
        sheets = SheetsService()
        
        # Verify sheet access
        logger.info("Step 4: Verifying spreadsheet access")
        if not sheets.verify_sheet_access():
            logger.error("Cannot access spreadsheet. Please check SPREADSHEET_ID in config.py")
            return
        
        # Ensure header row exists
        sheets.create_header_row()

        # Fetch existing message IDs from sheet to avoid duplicates on re-run
        logger.info("Step 5: Loading existing Message IDs from sheet for dedupe")
        sheet_message_ids = sheets.get_existing_message_ids()

        # Fetch unread emails
        logger.info("Step 6: Fetching unread emails from Gmail")
        raw_messages = gmail.fetch_unread_emails()
        
        if not raw_messages:
            logger.info("No unread emails found. Nothing to process.")
            return
        
        # Parse emails
        logger.info("Step 7: Parsing email content")
        parsed_emails = []
        for message in raw_messages:
            parsed = EmailParser.parse_email(message)
            if parsed:
                parsed_emails.append(parsed)
        
        if not parsed_emails:
            logger.warning("No emails could be parsed successfully")
            return
        
        # Filter out already processed emails
        logger.info("Step 8: Filtering new emails (deduplication across sheet + state)")
        new_emails = filter_new_emails(parsed_emails, state_manager, sheet_message_ids)
        
        if not new_emails:
            logger.info("No new emails to process (all already processed)")
            return
        
        # Prepare data for Sheets (remove message_id field)
        logger.info("Step 9: Preparing data for Google Sheets")
        emails_for_sheets = [
            {
                'message_id': email['message_id'],
                'from': email['from'],
                'subject': email['subject'],
                'date': email['date'],
                'content': email['content']
            }
            for email in new_emails
        ]
        
        # Append to Google Sheets
        logger.info(f"Step 10: Inserting {len(emails_for_sheets)} email(s) at top of Google Sheets")
        success = sheets.append_emails(emails_for_sheets)
        
        if not success:
            logger.error("Failed to append emails to Google Sheets")
            return
        
        # Mark emails as read in Gmail
        logger.info("Step 11: Marking emails as read in Gmail")
        message_ids = [email['message_id'] for email in new_emails]
        gmail.mark_multiple_as_read(message_ids)
        
        # Update state
        logger.info("Step 12: Updating state file")
        state_manager.mark_batch_processed(message_ids)
        state_manager.save_state()
        
        # Summary
        logger.info("=" * 60)
        logger.info("SUCCESS: Processing completed")
        logger.info(f"  - Fetched: {len(raw_messages)} unread email(s)")
        logger.info(f"  - New: {len(new_emails)} email(s)")
        logger.info(f"  - Inserted to Sheets: {len(emails_for_sheets)} row(s)")
        logger.info(f"  - Total processed (lifetime): {len(state_manager.processed_ids)}")
        logger.info("=" * 60)
    
    except FileNotFoundError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please ensure credentials.json is in the credentials/ folder")
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        logger.error("Processing failed. Check logs above for details.")


if __name__ == '__main__':
    main()
