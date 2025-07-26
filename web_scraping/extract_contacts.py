#!/usr/bin/env python3
"""
Extract Contact Information from Kirby Service Centers CSV
Extracts email addresses and names for email outreach campaigns.
"""

import csv
import re
import sys
from typing import List, Dict, Tuple

def clean_email(email: str) -> str:
    """Clean and validate email address"""
    if not email:
        return ""
    
    # Remove extra whitespace
    email = email.strip()
    
    # Basic email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_pattern, email):
        return email.lower()
    return ""

def extract_name_from_store(store_name: str) -> str:
    """Extract potential contact name from store name"""
    if not store_name:
        return ""
    
    # Remove common business suffixes
    suffixes = ['vacuum', 'service', 'center', 'repair', 'sales', 'store', 'shop']
    name = store_name.lower()
    
    for suffix in suffixes:
        name = name.replace(suffix, '').strip()
    
    # Clean up extra spaces and punctuation
    name = re.sub(r'\s+', ' ', name)
    name = re.sub(r'[^\w\s]', '', name)
    
    return name.title() if name else ""

def extract_contacts_from_csv(csv_file: str) -> List[Dict]:
    """Extract email addresses and names from CSV file"""
    contacts = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                # Extract email directly from Email column
                email = row.get('Email', '').strip()
                email = clean_email(email)
                
                # Extract store name from Name column
                store_name = row.get('Name', '').strip()
                name = extract_name_from_store(store_name)
                
                # Only add if we have an email
                if email:
                    contact = {
                        'email': email,
                        'name': name,
                        'store_name': store_name,
                        'address': f"{row.get('Street', '')}, {row.get('City/State/Zip', '')}",
                        'phone': row.get('Phone', ''),
                        'distance': row.get('Distance', ''),
                        'location': row.get('City/State/Zip', '').split(',')[0] if row.get('City/State/Zip') else ''
                    }
                    contacts.append(contact)
    
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found.")
        return []
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []
    
    return contacts

def save_contacts_to_csv(contacts: List[Dict], output_file: str):
    """Save extracted contacts to a new CSV file"""
    if not contacts:
        print("No contacts to save.")
        return
    
    fieldnames = ['email', 'name', 'store_name', 'address', 'phone', 'distance', 'location']
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(contacts)
        
        print(f"✅ Successfully saved {len(contacts)} contacts to '{output_file}'")
    
    except Exception as e:
        print(f"Error saving contacts: {e}")

def print_contact_summary(contacts: List[Dict]):
    """Print summary of extracted contacts"""
    if not contacts:
        print("❌ No valid email contacts found.")
        return
    
    print(f"\n📊 Contact Extraction Summary:")
    print(f"   Total contacts with emails: {len(contacts)}")
    
    # Count by location
    location_counts = {}
    for contact in contacts:
        location = contact.get('location', 'Unknown')
        location_counts[location] = location_counts.get(location, 0) + 1
    
    print(f"   Contacts by location:")
    for location, count in sorted(location_counts.items()):
        print(f"     {location}: {count}")
    
    # Show sample contacts
    print(f"\n📧 Sample contacts:")
    for i, contact in enumerate(contacts[:5]):
        print(f"   {i+1}. {contact['name']} ({contact['email']}) - {contact['store_name']}")

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python3 extract_contacts.py <csv_file>")
        print("Example: python3 extract_contacts.py kirby_service_centers_top_50_cities.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    output_file = csv_file.replace('.csv', '_contacts.csv')
    
    print(f"🔍 Extracting contacts from '{csv_file}'...")
    
    # Extract contacts
    contacts = extract_contacts_from_csv(csv_file)
    
    if contacts:
        # Print summary
        print_contact_summary(contacts)
        
        # Save to new CSV
        save_contacts_to_csv(contacts, output_file)
        
        print(f"\n📁 Contact file ready for email outreach: '{output_file}'")
    else:
        print("❌ No valid email contacts found in the CSV file.")

if __name__ == "__main__":
    main() 