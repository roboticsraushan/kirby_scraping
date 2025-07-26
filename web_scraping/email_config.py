# Email Configuration for Kirby Service Center Outreach
# Gmail API and Email Template Settings

import os
from typing import Dict, List

# Gmail API Configuration
GMAIL_CONFIG = {
    "credentials_file": "credentials.json",  # Download from Google Cloud Console
    "token_file": "token.json",            # Will be created after first auth
    "scopes": ["https://www.googleapis.com/auth/gmail.send"],
    "sender_email": "hello@nolon.ai",  # Company Gmail address
    "sender_name": "Raushan",  # Your name for the email
}

# Email Templates
EMAIL_TEMPLATES = {
    "kirby_partnership": {
        "subject": "Partnership Opportunity - {company_name}",
        "template": """
Dear {name},

I hope this email finds you well. My name is {sender_name} from {company_name}, and I'm reaching out regarding a potential partnership opportunity with your Kirby service center.

{business_description}

I noticed that {store_name} is an authorized Kirby service center, and I believe there could be mutual benefits in exploring a partnership. We specialize in innovative solutions and are looking to expand our network of trusted service providers.

**Why Partner with Us:**
• Access to cutting-edge technology solutions
• Increased revenue opportunities
• Enhanced service offerings for your customers

**What We Offer:**
• Custom automation solutions
• Technical support and training
• Marketing and business development support

Would you be interested in a brief 15-minute call to discuss how we might work together? I'm available at your convenience and would be happy to share more details about our partnership program.

Best regards,
{sender_name}
{company_name}
Phone: {phone_number}
Website: {website}
        """,
        "variables": ["name", "store_name", "sender_name", "business_description", "company_name", "phone_number", "website"]
    },
    
    "kirby_networking": {
        "subject": "Networking Opportunity - {company_name}",
        "template": """
Hello {name},

I hope you're having a great day! I'm {sender_name} from {company_name}, and I'm reaching out to connect with fellow Kirby service center professionals.

{business_description}

I came across {store_name} and was impressed by your service center's presence in the community. As someone who also works in the technology space, I believe there's value in building connections within our network.

**I'd love to:**
• Learn about your experience as a Kirby service center
• Share insights about automation and technology solutions
• Explore potential collaboration opportunities

Would you be open to a brief conversation? I'm flexible with timing and would be happy to accommodate your schedule.

Looking forward to connecting!

Best regards,
{sender_name}
{company_name}
Phone: {phone_number}
Website: {website}
        """,
        "variables": ["name", "store_name", "sender_name", "business_description", "company_name", "phone_number", "website"]
    },
    
    "kirby_business_development": {
        "subject": "Business Development Opportunity - {company_name}",
        "template": """
Dear {name},

I hope this message reaches you well. I'm {sender_name} from {company_name}, and I'm reaching out regarding a business development opportunity that could benefit {store_name}.

{business_description}

After researching your service center, I believe there's potential for a mutually beneficial partnership. We specialize in robotics automation and are actively seeking to collaborate with established Kirby service centers like yours.

**Partnership Benefits:**
• Increased revenue through new service offerings
• Access to cutting-edge automation technology
• Enhanced customer satisfaction and retention

**Our Track Record:**
• Successfully implemented automation solutions for 50+ businesses
• 95% client satisfaction rate
• 40% average efficiency improvement

I'd love to schedule a brief call to discuss this opportunity in detail. Would you be available for a 20-minute conversation this week?

Thank you for considering this partnership opportunity.

Best regards,
{sender_name}
{company_name}
Phone: {phone_number}
Website: {website}
        """,
        "variables": ["name", "store_name", "sender_name", "business_description", "company_name", "phone_number", "website"]
    }
}

# Email Campaign Settings
CAMPAIGN_SETTINGS = {
    "default_template": "kirby_partnership",
    "batch_size": 10,  # Send emails in batches to avoid rate limits
    "delay_between_batches": 60,  # Seconds between batches
    "delay_between_emails": 5,  # Seconds between individual emails
    "max_emails_per_day": 100,  # Gmail sending limits
    "test_mode": True,  # Set to False for actual sending
    "test_email": "",  # Your email for testing
}

# Email Personalization Options
PERSONALIZATION_OPTIONS = {
    "include_store_name": True,
    "include_location": True,
    "include_phone": False,
    "custom_greeting": True,
    "add_signature": True
}

# Email Tracking and Analytics
TRACKING_CONFIG = {
    "track_opens": True,
    "track_clicks": True,
    "track_bounces": True,
    "log_responses": True,
    "save_sent_emails": True
}

# Response Templates (for follow-ups)
RESPONSE_TEMPLATES = {
    "follow_up_1": {
        "subject": "Following up - Partnership Opportunity",
        "template": """
Hi {name},

I wanted to follow up on my previous email about the partnership opportunity with {store_name}. 

I understand you're busy, so I'll keep this brief. Would you be interested in a quick 10-minute call to discuss how we might work together?

If you're not interested, no worries - I appreciate your time.

Best regards,
{sender_name}
        """
    },
    
    "follow_up_2": {
        "subject": "Final follow-up - {store_name}",
        "template": """
Hi {name},

This is my final follow-up regarding the partnership opportunity with {store_name}.

If you're interested in learning more, please let me know. Otherwise, I'll remove you from my follow-up list.

Thanks for your time!

Best regards,
{sender_name}
        """
    }
}

# Email Validation and Filtering
EMAIL_FILTERS = {
    "exclude_domains": [
        "example.com",
        "test.com",
        "noreply.com",
        "no-reply.com"
    ],
    "exclude_keywords": [
        "noreply",
        "no-reply",
        "donotreply",
        "test"
    ],
    "min_name_length": 2,
    "max_name_length": 50
}

# Gmail API Setup Instructions
SETUP_INSTRUCTIONS = """
Gmail API Setup Instructions:

1. Go to Google Cloud Console (https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API for your project
4. Create credentials (OAuth 2.0 Client ID)
5. Download credentials.json and place in this directory
6. Update GMAIL_CONFIG with your email address
7. Run the email sender script for first-time authentication

Required Python packages:
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
"""

def get_template(template_name: str) -> Dict:
    """Get email template by name"""
    return EMAIL_TEMPLATES.get(template_name, EMAIL_TEMPLATES["kirby_partnership"])

def get_campaign_settings() -> Dict:
    """Get campaign settings"""
    return CAMPAIGN_SETTINGS.copy()

def validate_email_config() -> bool:
    """Validate email configuration"""
    if not GMAIL_CONFIG["sender_email"]:
        print("❌ Error: Please set sender_email in GMAIL_CONFIG")
        return False
    
    if not os.path.exists(GMAIL_CONFIG["credentials_file"]):
        print(f"❌ Error: {GMAIL_CONFIG['credentials_file']} not found")
        print("Please download credentials from Google Cloud Console")
        return False
    
    return True 