#!/usr/bin/env python3
"""
Email Preview - Shows email content from company to client
"""

import csv
from email_config import get_template, GMAIL_CONFIG

def preview_emails(csv_file: str, custom_subject: str = "", custom_body: str = ""):
    """Preview email content"""
    
    # Default angel outreach template if no custom content provided
    if not custom_subject and not custom_body:
        custom_subject = "Angel Investment Opportunity - {company_name} Update"
        custom_body = """Hi {name},

A quick update from our side, and all of this has happened just in the last few weeks: 

• Company is officially incorporated 
• We've finalized a live+work villa setup in Bangalore, [work-eat-sleep-repeat]
• Team's in motion: 4 interns onboarded, 2 full-time engineers joining soon
• Procurement for key hardware is underway
• MVP will be ready in 2 months[week-wise dev plan ready with contingency], and we kick off our first real-world pilot in Month 3 (in Bangalore), in a banglore it company washroom 

We're raising a ₹1.5–2 Cr angel round, got some commitment already, with ₹20L as minimum cheque size.

Would deeply appreciate if you could connect us with any angels who can bring patient capital to back a deeptech startup from India, for the world.

Will send over our updated vision slide + demo videos right after this — feel free to forward them!

Thanks a lot for your continued support 🙏"""
    
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
        
        # Create subject and body
        try:
            sender_name = contact.get('sender_name', 'Raushan').strip()  # Get from Excel file
            
            subject = custom_subject.format(
                name=name,
                sender_name=sender_name,
                company_name="Nolon AI"
            )
            
            body = custom_body.format(
                name=name,
                sender_name=sender_name,
                company_name="Nolon AI"
            )
        except KeyError as e:
            print(f"❌ Template placeholder error: {e}")
            return
        
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
    
    csv_file = "angel_investors_sample.csv"
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    
    preview_emails(csv_file)

if __name__ == "__main__":
    main()