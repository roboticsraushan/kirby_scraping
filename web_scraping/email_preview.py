#!/usr/bin/env python3
"""
Email Preview - Shows email content from company to client
"""

import csv
from email_config import get_template, GMAIL_CONFIG

def preview_emails(csv_file: str, template_name: str = "kirby_partnership"):
    """Preview email content"""
    
    # Get template
    template = get_template(template_name)
    
    print(f"📧 Email Preview - Company to Client")
    print(f"📁 File: {csv_file}")
    print(f"📤 From: {GMAIL_CONFIG['sender_email']} ({GMAIL_CONFIG['sender_name']})")
    print("=" * 60)
    
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
    print()
    
    # Preview first 3 emails
    for i, contact in enumerate(contacts[:3], 1):
        email = contact.get('email', '').strip()
        name = contact.get('name', 'there').strip()
        store_name = contact.get('store_name', 'your service center').strip()
        
        # Create subject
        subject = template["subject"].format(store_name=store_name)
        
        # Create body
        body = template["template"].format(
            name=name,
            store_name=store_name,
            sender_name=GMAIL_CONFIG["sender_name"]
        )
        
        print(f"📧 Email #{i}")
        print(f"   From: {GMAIL_CONFIG['sender_email']} (Company)")
        print(f"   To: {email} (Client)")
        print(f"   Subject: {subject}")
        print(f"   Body Preview:")
        print("   " + "-" * 40)
        print("   " + body[:300] + "...")
        print("   " + "-" * 40)
        print()
    
    if len(contacts) > 3:
        print(f"... and {len(contacts) - 3} more emails")
    
    print("✅ Preview complete - No emails were sent")

def main():
    """Main function"""
    import sys
    
    csv_file = "client_test_contacts.csv"
    template_name = "kirby_partnership"
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    if len(sys.argv) > 2:
        template_name = sys.argv[2]
    
    preview_emails(csv_file, template_name)

if __name__ == "__main__":
    main()