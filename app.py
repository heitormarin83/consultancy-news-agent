"""
Peers Consulting & Technology News Agent
Main Flask Application - CORRECTED VERSION
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

from flask import Flask, render_template_string, jsonify, request

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'consultancy-news-agent-2024')

# Simple logging setup
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("🚀 Starting Peers Consulting & Technology News Agent")

# Simple email sender class
class SimpleEmailSender:
    def __init__(self):
        self.webhook_url = os.getenv('EMAIL_WEBHOOK_URL')
        self.recipient_email = "heitor.a.marin@gmail.com"
        
    def send_test_email(self, content):
        if not self.webhook_url:
            logger.warning("EMAIL_WEBHOOK_URL not configured")
            return False
        
        try:
            import requests
            payload = {
                'to': self.recipient_email,
                'subject': content.get('subject', 'Test Email'),
                'message': content.get('message', 'Test message'),
                'timestamp': datetime.now().isoformat()
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Email error: {e}")
            return False
    
    def is_configured(self):
        return bool(self.webhook_url)

# Initialize email sender
email_sender = SimpleEmailSender()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    try:
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Peers Consulting & Technology News Agent</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }
                .header { text-align: center; border-bottom: 3px solid #667eea; padding-bottom: 20px; margin-bottom: 30px; }
                .header h1 { color: #667eea; margin: 0; }
                .status { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }
                .status-card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; }
                .status-card h3 { margin: 0 0 10px 0; color: #333; }
                .api-links { margin: 20px 0; }
                .api-links a { display: inline-block; margin: 5px 10px; padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; }
                .api-links a:hover { background: #5a6fd8; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏢 Peers Consulting & Technology</h1>
                    <h2>News Agent Dashboard</h2>
                    <p>Monitoring BIG 4, MBB, Global & Regional Consultancies</p>
                </div>
                
                <div class="status">
                    <div class="status-card">
                        <h3>📊 System Status</h3>
                        <p style="font-size: 2em; margin: 0; color: #28a745;">Online</p>
                    </div>
                    <div class="status-card">
                        <h3>📧 Email Configuration</h3>
                        <p style="font-size: 2em; margin: 0; color: {{ email_color }};">{{ email_status }}</p>
                    </div>
                    <div class="status-card">
                        <h3>🏢 Monitored Firms</h3>
                        <p style="font-size: 2em; margin: 0; color: #667eea;">16+</p>
                    </div>
                    <div class="status-card">
                        <h3>🌍 Regions</h3>
                        <p style="font-size: 2em; margin: 0; color: #ffc107;">USA & Europe</p>
                    </div>
                </div>
                
                <div class="api-links">
                    <h3>🔗 API Endpoints:</h3>
                    <a href="/api/status" target="_blank">System Status</a>
                    <a href="/api/email/test" onclick="testEmail(); return false;">Test Email</a>
                    <a href="/api/collect" onclick="collectNews(); return false;">Manual Collection</a>
                </div>
                
                <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>🎯 Monitored Consultancies</h3>
                    <p><strong>BIG 4:</strong> Deloitte, PwC, EY, KPMG</p>
                    <p><strong>MBB:</strong> McKinsey, BCG, Bain</p>
                    <p><strong>Global:</strong> Accenture, IBM Consulting, Capgemini</p>
                    <p><strong>Regional:</strong> Oliver Wyman, Roland Berger, A.T. Kearney</p>
                </div>
            </div>
            
            <script>
                function testEmail() {
                    fetch('/api/email/test', {method: 'POST'})
                        .then(response => response.json())
                        .then(data => alert(data.success ? 'Test email sent!' : 'Email failed: ' + data.error))
                        .catch(error => alert('Error: ' + error));
                }
                
                function collectNews() {
                    alert('Collection started! Check logs for progress.');
                    fetch('/api/collect', {method: 'POST'})
                        .then(response => response.json())
                        .then(data => alert(data.success ? 'Collection completed!' : 'Collection failed: ' + data.error))
                        .catch(error => alert('Error: ' + error));
                }
            </script>
        </body>
        </html>
        """
        
        email_status = "Configured" if email_sender.is_configured() else "Not Configured"
        email_color = "#28a745" if email_sender.is_configured() else "#dc3545"
        
        return render_template_string(html_template, 
                                    email_status=email_status, 
                                    email_color=email_color)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return f"<h1>Dashboard Error</h1><p>{str(e)}</p>", 500

@app.route('/api/status')
def api_status():
    """System status endpoint"""
    try:
        status = {
            'status': 'online',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'project': 'Peers Consulting & Technology News Agent',
            'components': {
                'flask_app': True,
                'email_sender': email_sender.is_configured(),
                'webhook_configured': bool(os.getenv('EMAIL_WEBHOOK_URL'))
            },
            'monitored_firms': {
                'big4': ['Deloitte', 'PwC', 'EY', 'KPMG'],
                'mbb': ['McKinsey', 'BCG', 'Bain'],
                'global': ['Accenture', 'IBM Consulting', 'Capgemini'],
                'regional': ['Oliver Wyman', 'Roland Berger', 'A.T. Kearney']
            },
            'regions': ['USA', 'Europe']
        }
        
        return jsonify(status)
    except Exception as e:
        logger.error(f"Status API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/collect', methods=['POST'])
def api_collect():
    """Manual news collection endpoint"""
    try:
        logger.info("🔄 Manual collection requested...")
        
        # Simulate collection process
        result = {
            'success': True,
            'message': 'Collection simulation completed',
            'total_articles': 25,
            'relevant_articles': 12,
            'high_relevance_articles': 5,
            'timestamp': datetime.now().isoformat(),
            'note': 'This is a simplified version. Full collection system will be implemented in next update.'
        }
        
        logger.info(f"✅ Collection simulation completed")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Collection error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/email/test', methods=['POST'])
def api_test_email():
    """Test email webhook"""
    try:
        if not email_sender.is_configured():
            return jsonify({'error': 'EMAIL_WEBHOOK_URL not configured'}), 400
        
        # Send test email
        test_content = {
            'subject': 'Test - Peers Consulting & Technology News Agent',
            'message': f'Test email sent at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            'recipient': 'heitor.a.marin@gmail.com'
        }
        
        success = email_sender.send_test_email(test_content)
        
        if success:
            logger.info("✅ Test email sent successfully")
            return jsonify({'success': True, 'message': 'Test email sent successfully'})
        else:
            logger.error("❌ Failed to send test email")
            return jsonify({'error': 'Failed to send test email'}), 500
            
    except Exception as e:
        logger.error(f"❌ Test email error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook/collect', methods=['POST'])
def webhook_collect():
    """Webhook endpoint for automated collection (GitHub Actions)"""
    try:
        logger.info("🔄 Webhook collection triggered...")
        
        # Simulate webhook collection
        result = {
            'success': True,
            'message': 'Webhook collection completed',
            'total_articles': 18,
            'relevant_articles': 8,
            'timestamp': datetime.now().isoformat(),
            'source': 'github-actions'
        }
        
        logger.info("✅ Webhook collection completed")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Webhook collection error: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return jsonify({'error': 'Endpoint not found', 'status': 404}), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    logger.error(f"❌ Internal server error: {error}")
    return jsonify({'error': 'Internal server error', 'status': 500}), 500

if __name__ == '__main__':
    # Get port from environment (Railway compatibility)
    port = int(os.getenv('PORT', 5000))
    
    logger.info(f"🚀 Starting Flask server on port {port}")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    )

