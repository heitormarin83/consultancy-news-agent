"""
Simplified Email System using Webhooks
Much easier than SMTP configuration!
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from ..utils.logger import get_logger

class WebhookEmailSender:
    """
    Simplified email sender using webhooks
    Only requires 1 environment variable: EMAIL_WEBHOOK_URL
    """
    
    def __init__(self):
        """Initialize webhook email sender"""
        self.logger = get_logger("webhook_sender")
        self.webhook_url = os.getenv('EMAIL_WEBHOOK_URL')
        self.recipient_email = "heitor.a.marin@gmail.com"
        
        if self.webhook_url:
            self.logger.info("✅ Webhook email sender initialized")
        else:
            self.logger.warning("⚠️ EMAIL_WEBHOOK_URL not configured - emails will not be sent")
    
    def send_daily_report(self, report_path: str) -> bool:
        """
        Send daily report via webhook
        
        Args:
            report_path: Path to the JSON report file
            
        Returns:
            bool: True if sent successfully
        """
        try:
            if not self.webhook_url:
                self.logger.warning("⚠️ Webhook URL not configured - skipping email")
                return False
            
            # Load report data
            if not Path(report_path).exists():
                self.logger.error(f"❌ Report file not found: {report_path}")
                return False
            
            with open(report_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            # Generate email content
            email_content = self._generate_daily_email_content(report_data)
            
            # Send via webhook
            success = self._send_webhook(email_content)
            
            if success:
                self.logger.info("✅ Daily report email sent successfully")
            else:
                self.logger.error("❌ Failed to send daily report email")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error sending daily report: {e}")
            return False
    
    def send_test_email(self, content: Dict[str, Any]) -> bool:
        """
        Send test email via webhook
        
        Args:
            content: Test email content
            
        Returns:
            bool: True if sent successfully
        """
        try:
            if not self.webhook_url:
                self.logger.warning("⚠️ Webhook URL not configured - skipping test email")
                return False
            
            # Prepare test email
            email_content = {
                'to': self.recipient_email,
                'subject': content.get('subject', 'Test Email'),
                'html': f"""
                <h2>🧪 Test Email - Peers Consulting & Technology</h2>
                <p><strong>Message:</strong> {content.get('message', 'Test message')}</p>
                <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                <p><strong>System:</strong> Consultancy News Agent</p>
                <hr>
                <p><em>This is a test email to verify webhook configuration.</em></p>
                """,
                'text': f"Test Email - {content.get('message', 'Test message')}"
            }
            
            # Send via webhook
            success = self._send_webhook(email_content)
            
            if success:
                self.logger.info("✅ Test email sent successfully")
            else:
                self.logger.error("❌ Failed to send test email")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error sending test email: {e}")
            return False
    
    def send_alert(self, alert_type: str, message: str) -> bool:
        """
        Send alert email via webhook
        
        Args:
            alert_type: Type of alert
            message: Alert message
            
        Returns:
            bool: True if sent successfully
        """
        try:
            if not self.webhook_url:
                self.logger.warning("⚠️ Webhook URL not configured - skipping alert")
                return False
            
            # Prepare alert email
            email_content = {
                'to': self.recipient_email,
                'subject': f'🚨 Alert - {alert_type} - Peers Consulting & Technology',
                'html': f"""
                <h2>🚨 System Alert</h2>
                <p><strong>Alert Type:</strong> {alert_type}</p>
                <p><strong>Message:</strong> {message}</p>
                <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                <hr>
                <p><em>Consultancy News Agent - Automated Alert</em></p>
                """,
                'text': f"Alert: {alert_type} - {message}"
            }
            
            # Send via webhook
            success = self._send_webhook(email_content)
            
            if success:
                self.logger.info(f"✅ Alert email sent: {alert_type}")
            else:
                self.logger.error(f"❌ Failed to send alert email: {alert_type}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error sending alert: {e}")
            return False
    
    def _generate_daily_email_content(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate daily email content from report data"""
        
        date = report_data.get('date', 'Unknown')
        total_articles = report_data.get('total_articles', 0)
        high_relevance = report_data.get('high_relevance_articles', 0)
        top_articles = report_data.get('top_articles', [])
        
        # Generate HTML content
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .stats {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .article {{ border-left: 4px solid #667eea; padding: 15px; margin: 15px 0; background: #f8f9fa; }}
                .article h3 {{ margin: 0 0 10px 0; color: #333; }}
                .article .meta {{ color: #666; font-size: 0.9em; margin: 5px 0; }}
                .article .score {{ background: #667eea; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; }}
                .footer {{ text-align: center; color: #666; font-size: 0.9em; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏢 Peers Consulting & Technology</h1>
                <h2>Daily News Report - {date}</h2>
            </div>
            
            <div class="content">
                <div class="stats">
                    <h3>📊 Daily Summary</h3>
                    <ul>
                        <li><strong>Total Articles Analyzed:</strong> {total_articles}</li>
                        <li><strong>High Relevance Articles:</strong> {high_relevance}</li>
                        <li><strong>Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</li>
                    </ul>
                </div>
        """
        
        # Add top articles
        if top_articles:
            html_content += "<h3>🔥 Top Relevant Articles</h3>"
            
            for i, article in enumerate(top_articles[:10], 1):
                title = article.get('title', 'No title')
                url = article.get('url', '#')
                source = article.get('source', 'Unknown')
                score = article.get('relevance_score', 0)
                firms = ', '.join(article.get('firms_mentioned', []))
                category = article.get('category', 'Other')
                
                html_content += f"""
                <div class="article">
                    <h3>{i}. <a href="{url}" target="_blank">{title}</a></h3>
                    <div class="meta">
                        <span class="score">Score: {score:.1f}</span>
                        <strong>Source:</strong> {source} | 
                        <strong>Category:</strong> {category}
                        {f' | <strong>Firms:</strong> {firms}' if firms else ''}
                    </div>
                </div>
                """
        else:
            html_content += "<p>No high-relevance articles found today.</p>"
        
        # Add footer
        html_content += f"""
            </div>
            
            <div class="footer">
                <p>📧 Consultancy News Agent | Automated Daily Report</p>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M UTC')}</p>
            </div>
        </body>
        </html>
        """
        
        # Generate text version
        text_content = f"""
        Peers Consulting & Technology - Daily News Report
        Date: {date}
        
        SUMMARY:
        - Total Articles: {total_articles}
        - High Relevance: {high_relevance}
        
        TOP ARTICLES:
        """
        
        for i, article in enumerate(top_articles[:5], 1):
            title = article.get('title', 'No title')
            url = article.get('url', '#')
            score = article.get('relevance_score', 0)
            text_content += f"\n{i}. {title}\n   Score: {score:.1f} | URL: {url}\n"
        
        return {
            'to': self.recipient_email,
            'subject': f'📊 Daily Consultancy Report - {date} ({high_relevance} high-relevance articles)',
            'html': html_content,
            'text': text_content
        }
    
    def _send_webhook(self, email_content: Dict[str, Any]) -> bool:
        """
        Send email via webhook
        
        Args:
            email_content: Email content dictionary
            
        Returns:
            bool: True if sent successfully
        """
        try:
            if not self.webhook_url:
                return False
            
            # Prepare webhook payload
            payload = {
                'email': email_content,
                'timestamp': datetime.now().isoformat(),
                'source': 'consultancy-news-agent'
            }
            
            # Send POST request to webhook
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Consultancy-News-Agent/1.0'
                },
                timeout=30
            )
            
            # Check response
            if response.status_code == 200:
                self.logger.info(f"✅ Webhook sent successfully: {response.status_code}")
                return True
            else:
                self.logger.error(f"❌ Webhook failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            self.logger.error("❌ Webhook timeout")
            return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Webhook request error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Unexpected webhook error: {e}")
            return False
    
    def is_configured(self) -> bool:
        """Check if webhook is configured"""
        return bool(self.webhook_url)
    
    def get_status(self) -> Dict[str, Any]:
        """Get webhook sender status"""
        return {
            'configured': self.is_configured(),
            'webhook_url_set': bool(self.webhook_url),
            'recipient': self.recipient_email,
            'type': 'webhook'
        }

