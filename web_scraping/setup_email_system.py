#!/usr/bin/env python3
"""
Setup Script for Email Outreach System
Helps configure Gmail API and install required packages.
"""

import os
import sys
import subprocess
from email_config import GMAIL_CONFIG, SETUP_INSTRUCTIONS

def install_required_packages():
    """Install required Python packages"""
    packages = [
        "google-auth",
        "google-auth-oauthlib", 
        "google-auth-httplib2",
        "google-api-python-client"
    ]
    
    print("📦 Installing required packages...")
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    
    return True

def check_gmail_config():
    """Check and guide Gmail API setup"""
    print("\n🔧 Gmail API Setup Check:")
    
    # Check credentials file
    if os.path.exists(GMAIL_CONFIG["credentials_file"]):
        print(f"✅ Found {GMAIL_CONFIG['credentials_file']}")
    else:
        print(f"❌ Missing {GMAIL_CONFIG['credentials_file']}")
        print("   Please download from Google Cloud Console")
    
    # Check sender email
    if GMAIL_CONFIG["sender_email"]:
        print(f"✅ Sender email configured: {GMAIL_CONFIG['sender_email']}")
    else:
        print("❌ Sender email not configured")
        print("   Please update GMAIL_CONFIG['sender_email'] in email_config.py")
    
    # Check sender name
    if GMAIL_CONFIG["sender_name"] != "Your Name":
        print(f"✅ Sender name configured: {GMAIL_CONFIG['sender_name']}")
    else:
        print("❌ Sender name not configured")
        print("   Please update GMAIL_CONFIG['sender_name'] in email_config.py")

def create_sample_contacts():
    """Create a sample contacts file for testing"""
    sample_contacts = [
        {
            'email': 'test1@example.com',
            'name': 'John Smith',
            'store_name': 'Smith Vacuum Service',
            'address': '123 Main St, Anytown, USA',
            'phone': '555-123-4567',
            'location': 'New York, NY'
        },
        {
            'email': 'test2@example.com', 
            'name': 'Jane Doe',
            'store_name': 'Doe Vacuum Center',
            'address': '456 Oak Ave, Somewhere, USA',
            'phone': '555-987-6543',
            'location': 'Los Angeles, CA'
        }
    ]
    
    import csv
    with open('sample_contacts.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['email', 'name', 'store_name', 'address', 'phone', 'location'])
        writer.writeheader()
        writer.writerows(sample_contacts)
    
    print("✅ Created sample_contacts.csv for testing")

def print_usage_instructions():
    """Print usage instructions"""
    print("\n📋 Usage Instructions:")
    print("\n1. Extract contacts from Kirby CSV:")
    print("   python3 extract_contacts.py kirby_service_centers_top_50_cities.csv")
    
    print("\n2. Test email system (test mode):")
    print("   python3 bulk_email_sender.py kirby_service_centers_top_50_cities_contacts.csv")
    
    print("\n3. Send actual emails (disable test mode in email_config.py):")
    print("   python3 bulk_email_sender.py kirby_service_centers_top_50_cities_contacts.csv kirby_partnership")
    
    print("\n4. Available email templates:")
    print("   - kirby_partnership")
    print("   - kirby_networking") 
    print("   - kirby_business_development")

def main():
    """Main setup function"""
    print("🚀 Email Outreach System Setup")
    print("=" * 40)
    
    # Install packages
    if not install_required_packages():
        print("❌ Package installation failed")
        sys.exit(1)
    
    # Check Gmail config
    check_gmail_config()
    
    # Create sample contacts
    create_sample_contacts()
    
    # Print setup instructions
    print("\n" + "=" * 40)
    print("📚 Gmail API Setup Instructions:")
    print(SETUP_INSTRUCTIONS)
    
    # Print usage
    print_usage_instructions()
    
    print("\n🎉 Setup complete! Follow the instructions above to get started.")

if __name__ == "__main__":
    main() 