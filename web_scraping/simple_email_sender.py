#!/usr/bin/env python3
"""
Simple Email Sender using SMTP
Bypasses Gmail API OAuth issues
"""

import smtplib
import csv
import time
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
from email_config import get_template, GMAIL_CONFIG
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_email_smtp(to_email, subject, body, sender_email, sender_password, attachments=None, html_body=None, embedded_images=None):
    """Send email using SMTP with optional attachments and embedded images"""
    try:
        # Create message
        msg = MIMEMultipart('related')
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Create alternative part for HTML and plain text
        msg_alternative = MIMEMultipart('alternative')
        msg.attach(msg_alternative)
        
        # Add plain text body
        msg_alternative.attach(MIMEText(body, 'plain'))
        
        # Add HTML body if provided
        if html_body:
            msg_alternative.attach(MIMEText(html_body, 'html'))
        
        # Add embedded images if provided
        if embedded_images:
            for image_path in embedded_images:
                if os.path.exists(image_path):
                    try:
                        with open(image_path, "rb") as image_file:
                            image_data = image_file.read()
                        
                        # Determine image type from file extension
                        image_ext = os.path.splitext(image_path)[1].lower()
                        if image_ext in ['.jpg', '.jpeg']:
                            image = MIMEImage(image_data, _subtype='jpeg')
                        elif image_ext == '.png':
                            image = MIMEImage(image_data, _subtype='png')
                        elif image_ext == '.gif':
                            image = MIMEImage(image_data, _subtype='gif')
                        else:
                            image = MIMEImage(image_data)
                        
                        image.add_header('Content-ID', f'<{os.path.basename(image_path)}>')
                        msg.attach(image)
                        print(f"✅ Embedded image: {os.path.basename(image_path)}")
                    except Exception as e:
                        print(f"❌ Error embedding image {image_path}: {e}")
        
        # Add attachments if provided
        if attachments:
            for attachment_path in attachments:
                if os.path.exists(attachment_path):
                    try:
                        with open(attachment_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        
                        # Set proper MIME type based on file extension
                        file_ext = os.path.splitext(attachment_path)[1].lower()
                        if file_ext == '.pdf':
                            part.add_header('Content-Type', 'application/pdf')
                        elif file_ext in ['.doc', '.docx']:
                            part.add_header('Content-Type', 'application/msword' if file_ext == '.doc' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                        elif file_ext == '.zip':
                            part.add_header('Content-Type', 'application/zip')
                        elif file_ext == '.rar':
                            part.add_header('Content-Type', 'application/x-rar-compressed')
                        elif file_ext == '.7z':
                            part.add_header('Content-Type', 'application/x-7z-compressed')
                        elif file_ext in ['.xls', '.xlsx']:
                            part.add_header('Content-Type', 'application/vnd.ms-excel' if file_ext == '.xls' else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                        elif file_ext == '.txt':
                            part.add_header('Content-Type', 'text/plain')
                        
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(attachment_path)}'
                        )
                        msg.attach(part)
                        print(f"✅ Attached: {os.path.basename(attachment_path)}")
                    except Exception as e:
                        print(f"❌ Error attaching {attachment_path}: {e}")
        
        # Create SMTP session
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        # Login
        server.login(sender_email, sender_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
        
        print(f"✅ Email sent to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
        return False

def send_bulk_emails_smtp(csv_file, template_name="kirby_partnership", sender_password=""):
    """Send bulk emails using SMTP"""
    
    if not sender_password:
        print("❌ Please provide your Gmail app password")
        print("   Go to: https://myaccount.google.com/apppasswords")
        print("   Generate an app password for this application")
        return
    
    # Get template
    template = get_template(template_name)
    sender_email = GMAIL_CONFIG["sender_email"]
    
    print(f"📧 Starting SMTP email campaign...")
    print(f"   Template: {template_name}")
    print(f"   Sender: {sender_email}")
    print(f"   File: {csv_file}")
    
    # Read contacts
    contacts = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            contacts = list(reader)
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return
    
    print(f"📊 Found {len(contacts)} contacts")
    
    # Send emails
    sent_count = 0
    failed_count = 0
    
    for i, contact in enumerate(contacts, 1):
        email = contact.get('email', '').strip()
        name = contact.get('name', 'there').strip()
        store_name = contact.get('store_name', 'your service center').strip()
        
        # Create subject and body
        subject = template["subject"].format(store_name=store_name)
        body = template["template"].format(
            name=name,
            store_name=store_name,
            sender_name=GMAIL_CONFIG["sender_name"]
        )
        
        print(f"\n📧 Sending email {i}/{len(contacts)} to {email}")
        print(f"   Subject: {subject}")
        
        # Send email
        success = send_email_smtp(email, subject, body, sender_email, sender_password)
        
        if success:
            sent_count += 1
        else:
            failed_count += 1
        
        # Delay between emails
        if i < len(contacts):
            print("⏳ Waiting 5 seconds...")
            time.sleep(5)
    
    print(f"\n🎉 Campaign completed!")
    print(f"   ✅ Sent: {sent_count}")
    print(f"   ❌ Failed: {failed_count}")

def main():
    """Main function"""
    import sys
    
    csv_file = "client_test_contacts.csv"
    template_name = "kirby_partnership"
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    if len(sys.argv) > 2:
        template_name = sys.argv[2]
    
    # Get credentials from environment variables
    sender_password = os.getenv('GMAIL_APP_PASSWORD')
    sender_email = os.getenv('SENDER_EMAIL', GMAIL_CONFIG["sender_email"])
    sender_name = os.getenv('SENDER_NAME', GMAIL_CONFIG["sender_name"])
    
    if not sender_password:
        print("❌ Gmail App Password not found in .env file")
        print("   Please add GMAIL_APP_PASSWORD=your_password to .env file")
        return
    
    print(f"🔐 Using credentials from .env file")
    print(f"   Email: {sender_email}")
    print(f"   Name: {sender_name}")
    print(f"   Password: {'*' * len(sender_password)}")
    print()
    
    send_bulk_emails_smtp(csv_file, template_name, sender_password)

if __name__ == "__main__":
    main() 