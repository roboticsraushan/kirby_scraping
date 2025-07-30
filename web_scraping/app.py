#!/usr/bin/env python3
"""
Email Campaign Web Interface
Flask-based web application for bulk email campaigns
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import csv
import json
import time
import threading
from datetime import datetime
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from email_config import get_template, CAMPAIGN_SETTINGS
from simple_email_sender import send_email_smtp

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create uploads directory
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global campaign state
campaign_status = {
    'running': False,
    'total': 0,
    'sent': 0,
    'failed': 0,
    'current_email': '',
    'progress': 0,
    'logs': []
}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def log_message(message, level='info'):
    """Add log message to campaign status"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    campaign_status['logs'].append({
        'timestamp': timestamp,
        'message': message,
        'level': level
    })
    # Keep only last 50 logs
    if len(campaign_status['logs']) > 50:
        campaign_status['logs'] = campaign_status['logs'][-50:]

def send_campaign_emails(csv_file, custom_subject, custom_body):
    """Send campaign emails in background thread"""
    global campaign_status
    
    try:
        # Read CSV file
        contacts = []
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            contacts = list(reader)
        
        campaign_status['total'] = len(contacts)
        campaign_status['sent'] = 0
        campaign_status['failed'] = 0
        campaign_status['running'] = True
        
        log_message(f"Starting campaign with {len(contacts)} contacts", 'info')
        
        # Get credentials
        sender_password = os.getenv('GMAIL_APP_PASSWORD')
        sender_email = os.getenv('SENDER_EMAIL', 'hello@nolon.ai')
        
        if not sender_password:
            log_message("Gmail App Password not found in .env file", 'error')
            campaign_status['running'] = False
            return
        
        # Send emails
        for i, contact in enumerate(contacts, 1):
            if not campaign_status['running']:
                log_message("Campaign stopped by user", 'warning')
                break
                
            email = contact.get('email', '').strip()
            name = contact.get('name', 'there').strip()
            sender_name = contact.get('sender_name', 'Raushan').strip()  # Get from Excel file
            
            # Create subject and body with custom template
            try:
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
                log_message(f"Template placeholder error: {e}", 'error')
                campaign_status['failed'] += 1
                continue
            
            campaign_status['current_email'] = email
            campaign_status['progress'] = (i / len(contacts)) * 100
            
            log_message(f"Sending email {i}/{len(contacts)} to {email}", 'info')
            
            # Send email
            success = send_email_smtp(email, subject, body, sender_email, sender_password)
            
            if success:
                campaign_status['sent'] += 1
                log_message(f"✅ Email sent to {email}", 'success')
            else:
                campaign_status['failed'] += 1
                log_message(f"❌ Failed to send to {email}", 'error')
            
            # Delay between emails
            if i < len(contacts):
                time.sleep(5)
        
        log_message(f"Campaign completed! Sent: {campaign_status['sent']}, Failed: {campaign_status['failed']}", 'info')
        
    except Exception as e:
        log_message(f"Campaign error: {str(e)}", 'error')
    finally:
        campaign_status['running'] = False

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Read CSV to get preview
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                contacts = list(reader)
                
            preview = contacts  # Show all contacts
            
            return jsonify({
                'success': True,
                'filename': filename,
                'total_contacts': len(contacts),
                'preview': preview,
                'columns': list(contacts[0].keys()) if contacts else []
            })
        except Exception as e:
            return jsonify({'error': f'Error reading CSV: {str(e)}'}), 400
    
    return jsonify({'error': 'Invalid file type'}), 400



@app.route('/start_campaign', methods=['POST'])
def start_campaign():
    """Start email campaign"""
    data = request.json
    
    if campaign_status['running']:
        return jsonify({'error': 'Campaign already running'}), 400
    
    csv_file = os.path.join(app.config['UPLOAD_FOLDER'], data['filename'])
    custom_subject = data.get('custom_subject', '')
    custom_body = data.get('custom_body', '')
    
    if not os.path.exists(csv_file):
        return jsonify({'error': 'CSV file not found'}), 400
    
    # Start campaign in background thread
    thread = threading.Thread(
        target=send_campaign_emails,
        args=(csv_file, custom_subject, custom_body)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': 'Campaign started'})

@app.route('/stop_campaign', methods=['POST'])
def stop_campaign():
    """Stop email campaign"""
    campaign_status['running'] = False
    return jsonify({'success': True, 'message': 'Campaign stopped'})

@app.route('/status')
def get_status():
    """Get campaign status"""
    return jsonify(campaign_status)

@app.route('/logs')
def get_logs():
    """Get campaign logs"""
    return jsonify({'logs': campaign_status['logs']})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 