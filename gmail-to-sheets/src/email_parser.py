"""
Email Parser Module
Extracts email metadata and content from Gmail API message objects.
"""

import base64
import logging
from datetime import datetime
from typing import Dict, Optional
import email
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class EmailParser:
    """
    Parser for Gmail API message objects.
    Extracts sender, subject, date, and plain text body.
    """
    
    @staticmethod
    def parse_email(message: Dict) -> Optional[Dict[str, str]]:
        """
        Parse a Gmail API message object into structured data.
        
        Args:
            message: Full Gmail message object from API
        
        Returns:
            Dictionary with keys: message_id, from, subject, date, content
            Returns None if parsing fails
        """
        try:
            message_id = message.get('id', '')
            payload = message.get('payload', {})
            headers = payload.get('headers', [])
            
            # Extract headers
            sender = EmailParser._get_header(headers, 'From')
            subject = EmailParser._get_header(headers, 'Subject')
            date_str = EmailParser._get_header(headers, 'Date')
            
            # Parse date to readable format
            date = EmailParser._parse_date(date_str)
            
            # Extract email body (plain text)
            content = EmailParser._extract_body(payload)
            
            parsed_data = {
                'message_id': message_id,
                'from': sender,
                'subject': subject or '(No Subject)',
                'date': date,
                'content': content
            }
            
            logger.debug(f"Successfully parsed email: {message_id}")
            return parsed_data
        
        except Exception as e:
            logger.error(f"Error parsing email: {e}")
            return None
    
    @staticmethod
    def _get_header(headers: list, name: str) -> str:
        """
        Extract a specific header value from headers list.
        
        Args:
            headers: List of header dictionaries
            name: Header name to search for
        
        Returns:
            Header value or empty string if not found
        """
        for header in headers:
            if header.get('name', '').lower() == name.lower():
                return header.get('value', '')
        return ''
    
    @staticmethod
    def _parse_date(date_str: str) -> str:
        """
        Parse email date string to readable format.
        
        Args:
            date_str: Raw date string from email header
        
        Returns:
            Formatted date string (YYYY-MM-DD HH:MM:SS)
        """
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            # Parse email date format (RFC 2822)
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            logger.warning(f"Could not parse date '{date_str}': {e}")
            return date_str[:50]  # Return truncated original
    
    @staticmethod
    def _extract_body(payload: Dict) -> str:
        """
        Extract plain text body from email payload.
        
        Handles:
        - Plain text parts
        - HTML parts (converted to plain text)
        - Multipart messages
        - Base64 encoded content
        
        Args:
            payload: Gmail message payload
        
        Returns:
            Plain text email body
        """
        body = ''
        
        # Check if message has parts (multipart)
        if 'parts' in payload:
            body = EmailParser._extract_from_parts(payload['parts'])
        else:
            # Single part message
            body = EmailParser._decode_body(payload)
        
        # Clean up the body
        body = EmailParser._clean_text(body)
        
        return body or '(No content)'
    
    @staticmethod
    def _extract_from_parts(parts: list) -> str:
        """
        Extract body from multipart message.
        
        Priority: text/plain > text/html
        
        Args:
            parts: List of message parts
        
        Returns:
            Extracted plain text
        """
        plain_text = ''
        html_text = ''
        
        for part in parts:
            mime_type = part.get('mimeType', '')
            
            # Recursive handling for nested parts
            if 'parts' in part:
                nested = EmailParser._extract_from_parts(part['parts'])
                if nested:
                    return nested
            
            # Extract based on MIME type
            if mime_type == 'text/plain':
                plain_text = EmailParser._decode_body(part)
                if plain_text:
                    return plain_text  # Prefer plain text
            
            elif mime_type == 'text/html':
                html_text = EmailParser._decode_body(part)
        
        # Fallback to HTML if no plain text found
        if html_text and not plain_text:
            return EmailParser._html_to_text(html_text)
        
        return plain_text or html_text
    
    @staticmethod
    def _decode_body(part: Dict) -> str:
        """
        Decode base64 encoded body data.
        
        Args:
            part: Message part containing body data
        
        Returns:
            Decoded text
        """
        body_data = part.get('body', {}).get('data', '')
        
        if not body_data:
            return ''
        
        try:
            # Gmail API uses URL-safe base64 encoding
            decoded = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
            return decoded
        except Exception as e:
            logger.warning(f"Error decoding body: {e}")
            return ''
    
    @staticmethod
    def _html_to_text(html: str) -> str:
        """
        Convert HTML to plain text.
        
        Args:
            html: HTML string
        
        Returns:
            Plain text extracted from HTML
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style']):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            logger.warning(f"Error converting HTML to text: {e}")
            return html  # Return raw HTML as fallback
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text
        
        Returns:
            Cleaned text
        """
        if not text:
            return ''
        
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Truncate if too long (Google Sheets cell limit is 50,000 chars)
        MAX_LENGTH = 40000
        if len(text) > MAX_LENGTH:
            text = text[:MAX_LENGTH] + '\n\n... [Content truncated]'
        
        return text.strip()


def parse_email_batch(messages: list) -> list:
    """
    Parse multiple email messages.
    
    Args:
        messages: List of Gmail message objects
    
    Returns:
        List of parsed email dictionaries
    """
    parsed_emails = []
    
    for message in messages:
        parsed = EmailParser.parse_email(message)
        if parsed:
            parsed_emails.append(parsed)
    
    logger.info(f"Parsed {len(parsed_emails)}/{len(messages)} emails successfully")
    return parsed_emails
