#!/usr/bin/env python3
"""
Bulk Email Sender for Kirby Service Center Outreach
Uses Gmail API to send personalized emails to extracted contacts.
"""

import csv
import json
import time
import base64
import sys
from typing import List, Dict, Optional
from datetime import datetime, timedelta

# Gmail API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("❌ Error: Gmail API packages not installed.")
    print("Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

# Import our configuration
from email_config import (
    GMAIL_CONFIG, 
    EMAIL_TEMPLATES, 
    CAMPAIGN_SETTINGS,
    PERSONALIZATION_OPTIONS,
    EMAIL_FILTERS,
    get_template,
    get_campaign_settings,
    validate_email_config
)

class BulkEmailSender:
    def __init__(self):
        self.service = None
        self.sent_emails = []
        self.failed_emails = []
        self.campaign_settings = get_campaign_settings()
        
    def authenticate_gmail(self):
        """Authenticate with Gmail API"""
        creds = None
        
        # Load existing token
        if os.path.exists(GMAIL_CONFIG["token_file"]):
            creds = Credentials.from_authorized_user_file(
                GMAIL_CONFIG["token_file"], 
                GMAIL_CONFIG["scopes"]
            )
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    GMAIL_CONFIG["credentials_file"], 
                    GMAIL_CONFIG["scopes"]
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(GMAIL_CONFIG["token_file"], 'w') as token:
                token.write(creds.to_json())
        
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            print("✅ Gmail API authenticated successfully")
            return True
        except Exception as e:
            print(f"❌ Gmail API authentication failed: {e}")
            return False
    
    def validate_email(self, email: str) -> bool:
        """Validate email address"""
        if not email or '@' not in email:
            return False
        
        domain = email.split('@')[1].lower()
        
        # Check excluded domains
        if domain in EMAIL_FILTERS["exclude_domains"]:
            return False
        
        # Check excluded keywords
        for keyword in EMAIL_FILTERS["exclude_keywords"]:
            if keyword.lower() in email.lower():
                return False
        
        return True
    
    def load_contacts(self, csv_file: str) -> List[Dict]:
        """Load contacts from CSV file"""
        contacts = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    email = row.get('email', '').strip()
                    
                    if self.validate_email(email):
                        contact = {
                            'email': email,
                            'name': row.get('name', '').strip(),
                            'store_name': row.get('store_name', '').strip(),
                            'address': row.get('address', '').strip(),
                            'phone': row.get('phone', '').strip(),
                            'location': row.get('location', '').strip()
                        }
                        contacts.append(contact)
        
        except FileNotFoundError:
            print(f"❌ Error: CSV file '{csv_file}' not found.")
            return []
        except Exception as e:
            print(f"❌ Error reading CSV file: {e}")
            return []
        
        print(f"✅ Loaded {len(contacts)} valid contacts from '{csv_file}'")
        return contacts
    
    def personalize_email(self, template: str, contact: Dict) -> str:
        """Personalize email template with contact data"""
        # Basic personalization
        personalized = template.format(
            name=contact.get('name', 'there'),
            store_name=contact.get('store_name', 'your service center'),
            sender_name=GMAIL_CONFIG["sender_name"]
        )
        
        # Add location if enabled
        if PERSONALIZATION_OPTIONS["include_location"] and contact.get('location'):
            personalized = personalized.replace(
                "[LOCATION]", 
                contact.get('location', '')
            )
        
        return personalized
    
    def create_email_message(self, to_email: str, subject: str, body: str) -> Dict:
        """Create Gmail API message format"""
        message = {
            'raw': base64.urlsafe_b64encode(
                f"To: {to_email}\r\n"
                f"From: {GMAIL_CONFIG['sender_email']}\r\n"
                f"Subject: {subject}\r\n"
                f"Content-Type: text/plain; charset=utf-8\r\n"
                f"\r\n"
                f"{body}".encode('utf-8')
            ).decode('utf-8')
        }
        return message
    
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send single email via Gmail API"""
        try:
            message = self.create_email_message(to_email, subject, body)
            
            if self.campaign_settings["test_mode"]:
                # In test mode, just log the email
                print(f"📧 TEST MODE - Would send to: {to_email}")
                print(f"   Subject: {subject}")
                print(f"   Body: {body[:100]}...")
                return True
            
            # Send actual email
            sent_message = self.service.users().messages().send(
                userId='me', 
                body=message
            ).execute()
            
            print(f"✅ Email sent to {to_email} (Message ID: {sent_message['id']})")
            return True
            
        except HttpError as error:
            print(f"❌ Failed to send email to {to_email}: {error}")
            return False
        except Exception as e:
            print(f"❌ Error sending email to {to_email}: {e}")
            return False
    
    def send_bulk_emails(self, contacts: List[Dict], template_name: str = None):
        """Send bulk emails to contacts"""
        if not contacts:
            print("❌ No contacts to send emails to.")
            return
        
        # Get template
        template_name = template_name or self.campaign_settings["default_template"]
        template = get_template(template_name)
        
        print(f"📧 Starting bulk email campaign...")
        print(f"   Template: {template_name}")
        print(f"   Contacts: {len(contacts)}")
        print(f"   Test Mode: {self.campaign_settings['test_mode']}")
        
        # Process contacts in batches
        batch_size = self.campaign_settings["batch_size"]
        total_sent = 0
        
        for i in range(0, len(contacts), batch_size):
            batch = contacts[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(contacts) + batch_size - 1) // batch_size
            
            print(f"\n📦 Processing batch {batch_num}/{total_batches} ({len(batch)} contacts)")
            
            for j, contact in enumerate(batch, 1):
                # Personalize email
                subject = template["subject"].format(
                    store_name=contact.get('store_name', 'your service center')
                )
                body = self.personalize_email(template["template"], contact)
                
                # Send email
                success = self.send_email(contact['email'], subject, body)
                
                if success:
                    self.sent_emails.append({
                        'email': contact['email'],
                        'name': contact['name'],
                        'store_name': contact['store_name'],
                        'timestamp': datetime.now().isoformat(),
                        'subject': subject
                    })
                    total_sent += 1
                else:
                    self.failed_emails.append({
                        'email': contact['email'],
                        'name': contact['name'],
                        'store_name': contact['store_name'],
                        'error': 'Failed to send'
                    })
                
                # Delay between emails
                if j < len(batch):
                    time.sleep(self.campaign_settings["delay_between_emails"])
            
            # Delay between batches
            if i + batch_size < len(contacts):
                print(f"⏳ Waiting {self.campaign_settings['delay_between_batches']} seconds before next batch...")
                time.sleep(self.campaign_settings["delay_between_batches"])
        
        # Save results
        self.save_campaign_results()
        
        print(f"\n🎉 Campaign completed!")
        print(f"   ✅ Sent: {total_sent}")
        print(f"   ❌ Failed: {len(self.failed_emails)}")
    
    def save_campaign_results(self):
        """Save campaign results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save sent emails
        if self.sent_emails:
            sent_file = f"sent_emails_{timestamp}.csv"
            with open(sent_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=['email', 'name', 'store_name', 'timestamp', 'subject'])
                writer.writeheader()
                writer.writerows(self.sent_emails)
            print(f"📁 Sent emails saved to: {sent_file}")
        
        # Save failed emails
        if self.failed_emails:
            failed_file = f"failed_emails_{timestamp}.csv"
            with open(failed_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=['email', 'name', 'store_name', 'error'])
                writer.writeheader()
                writer.writerows(self.failed_emails)
            print(f"📁 Failed emails saved to: {failed_file}")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python3 bulk_email_sender.py <contacts_csv> [template_name]")
        print("Example: python3 bulk_email_sender.py kirby_contacts.csv kirby_partnership")
        sys.exit(1)
    
    contacts_file = sys.argv[1]
    template_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Validate configuration
    if not validate_email_config():
        sys.exit(1)
    
    # Initialize sender
    sender = BulkEmailSender()
    
    # Authenticate with Gmail
    if not sender.authenticate_gmail():
        sys.exit(1)
    
    # Load contacts
    contacts = sender.load_contacts(contacts_file)
    if not contacts:
        sys.exit(1)
    
    # Send bulk emails
    sender.send_bulk_emails(contacts, template_name)

if __name__ == "__main__":
    import os
    main() 