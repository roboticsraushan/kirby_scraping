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
from docx import Document

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'docx', 'doc'}
ALLOWED_ATTACHMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif', 'xlsx', 'xls', 'zip', 'rar', '7z'}
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

def allowed_attachment_file(filename):
    """Check if attachment file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_ATTACHMENT_EXTENSIONS

def read_doc_file(filepath):
    """Read content from DOC/DOCX file and extract images with formatting"""
    try:
        doc = Document(filepath)
        html_content = []
        images = []
        
        # Extract content with formatting
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                # Check for bold text
                runs_html = []
                for run in paragraph.runs:
                    text = run.text
                    if run.bold:
                        text = f'<strong>{text}</strong>'
                    if run.italic:
                        text = f'<em>{text}</em>'
                    if run.underline:
                        text = f'<u>{text}</u>'
                    runs_html.append(text)
                
                paragraph_html = ''.join(runs_html)
                if paragraph_html.strip():
                    html_content.append(f'<p>{paragraph_html}</p>')
        
        # Extract images if any
        for rel in doc.part.rels.values():
            if "image" in rel.target_ref:
                try:
                    image_data = rel.target_part.blob
                    image_filename = f"image_{len(images)}.png"
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
                    
                    with open(image_path, 'wb') as f:
                        f.write(image_data)
                    
                    images.append(image_path)
                    # Add image to HTML content
                    html_content.append(f'<img src="cid:{image_filename}" style="max-width: 100%; height: auto; display: block; margin: 10px 0;">')
                except Exception as e:
                    print(f"Warning: Could not extract image: {e}")
        
        # Create complete HTML document
        html_body = f'''
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }}
                p {{ margin: 10px 0; }}
                img {{ max-width: 100%; height: auto; display: block; margin: 10px 0; }}
            </style>
        </head>
        <body>
            {''.join(html_content)}
        </body>
        </html>
        '''
        
        # Also create plain text version
        plain_text = '\n\n'.join([p.replace('<p>', '').replace('</p>', '').replace('<strong>', '').replace('</strong>', '').replace('<em>', '').replace('</em>', '').replace('<u>', '').replace('</u>', '') for p in html_content])
        
        return {
            'text': plain_text,
            'html': html_body,
            'images': images
        }
    except Exception as e:
        raise Exception(f"Error reading DOC file: {str(e)}")

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

def send_campaign_emails(csv_file, custom_subject, custom_body, attachments=None, embedded_images=None, html_content=None):
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
        if attachments:
            log_message(f"Attachments: {len(attachments)} files", 'info')
        if embedded_images:
            log_message(f"Embedded images: {len(embedded_images)} files", 'info')
        if html_content:
            log_message(f"Using HTML content from DOC file", 'info')
        
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
            
            # Create HTML body
            html_body = None
            if html_content:
                # Use HTML content from DOC file and replace placeholders
                html_body = html_content
                html_body = html_body.replace('{name}', name)
                html_body = html_body.replace('{sender_name}', sender_name)
                html_body = html_body.replace('{company_name}', 'Nolon AI')
            elif embedded_images:
                # Convert plain text to HTML
                html_body = f'<html><body style="font-family: Arial, sans-serif; line-height: 1.6;">'
                html_body += body.replace('\n', '<br>')
                
                # Add images after the text
                for j, image_path in enumerate(embedded_images):
                    image_filename = os.path.basename(image_path)
                    html_body += f'<br><img src="cid:{image_filename}" style="max-width: 100%; height: auto; display: block; margin: 10px 0;"><br>'
                
                html_body += '</body></html>'
            
            campaign_status['current_email'] = email
            campaign_status['progress'] = (i / len(contacts)) * 100
            
            log_message(f"Sending email {i}/{len(contacts)} to {email}", 'info')
            if embedded_images:
                log_message(f"Embedding {len(embedded_images)} images: {[os.path.basename(img) for img in embedded_images]}", 'info')
            
            # Send email with attachments and embedded images
            success = send_email_smtp(email, subject, body, sender_email, sender_password, attachments, html_body, embedded_images)
            
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
        
        # Check if it's a DOC file
        file_ext = filename.rsplit('.', 1)[1].lower()
        if file_ext in ['docx', 'doc']:
            # Read DOC file content
            try:
                doc_content = read_doc_file(filepath)
                return jsonify({
                    'success': True,
                    'filename': filename,
                    'file_type': 'doc',
                    'content': doc_content['text'],
                    'html_content': doc_content['html'],
                    'images': doc_content['images']
                })
            except Exception as e:
                return jsonify({'error': f'Error reading DOC file: {str(e)}'}), 400
        else:
            # Read CSV to get preview
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    contacts = list(reader)
                    
                preview = contacts  # Show all contacts
                
                return jsonify({
                    'success': True,
                    'filename': filename,
                    'file_type': 'csv',
                    'total_contacts': len(contacts),
                    'preview': preview,
                    'columns': list(contacts[0].keys()) if contacts else []
                })
            except Exception as e:
                return jsonify({'error': f'Error reading CSV: {str(e)}'}), 400
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/upload_attachment', methods=['POST'])
def upload_attachment():
    """Handle attachment file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_attachment_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath
        })
    
    return jsonify({'error': 'Invalid attachment file type'}), 400



@app.route('/start_campaign', methods=['POST'])
def start_campaign():
    """Start email campaign"""
    data = request.json
    
    if campaign_status['running']:
        return jsonify({'error': 'Campaign already running'}), 400
    
    csv_file = os.path.join(app.config['UPLOAD_FOLDER'], data['filename'])
    custom_subject = data.get('custom_subject', '')
    custom_body = data.get('custom_body', '')
    attachments = data.get('attachments', [])
    embedded_images = data.get('embedded_images', [])
    html_content = data.get('html_content', '')
    
    # Debug: Log what we received
    print(f"🔍 Campaign start request:")
    print(f"   CSV file: {data['filename']}")
    print(f"   Attachments: {attachments}")
    print(f"   Embedded images: {embedded_images}")
    print(f"   Subject length: {len(custom_subject)}")
    print(f"   Body length: {len(custom_body)}")
    print(f"   HTML content length: {len(html_content)}")
    
    if not os.path.exists(csv_file):
        return jsonify({'error': 'CSV file not found'}), 400
    
    # Convert attachment filenames to full paths
    attachment_paths = []
    for attachment in attachments:
        attachment_path = os.path.join(app.config['UPLOAD_FOLDER'], attachment)
        if os.path.exists(attachment_path):
            attachment_paths.append(attachment_path)
    
    # Convert embedded image filenames to full paths
    embedded_image_paths = []
    for image in embedded_images:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image)
        if os.path.exists(image_path):
            embedded_image_paths.append(image_path)
    
    # Start campaign in background thread
    thread = threading.Thread(
        target=send_campaign_emails,
        args=(csv_file, custom_subject, custom_body, attachment_paths, embedded_image_paths, html_content)
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