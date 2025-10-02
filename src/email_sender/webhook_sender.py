"""
Ultra-Simple Email System using ntfy.sh
Zero configuration required - works immediately!
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
    Ultra-simple email sender using ntfy.sh
    No configuration required - works out of the box!
    """
    
    def __init__(self):
        """Initialize ntfy.sh email sender"""
        self.logger = get_logger("ntfy_sender")
        self.recipient_email = "heitor.a.marin@gmail.com"
        
        # ntfy.sh topic for this project
        self.ntfy_topic = "consultancy-news-agent-heitor"
        self.ntfy_url = f"https://ntfy.sh/{self.ntfy_topic}"
        
        # Test connection
        self._test_connection()
        
        self.logger.info("✅ ntfy.sh email sender initialized")
        self.logger.info(f"📱 Subscribe to notifications: https://ntfy.sh/{self.ntfy_topic}")
    
    def _test_connection(self):
        """Test ntfy.sh connection"""
        try:
            response = requests.get("https://ntfy.sh", timeout=5)
            if response.status_code == 200:
                self.logger.info("✅ ntfy.sh service available")
                return True
        except Exception as e:
            self.logger.warning(f"⚠️ ntfy.sh connection test failed: {e}")
        return False
    
    def send_daily_report(self, report_path: str) -> bool:
        """
        Send daily report via ntfy.sh
        
        Args:
            report_path: Path to the JSON report file
            
        Returns:
            bool: True if sent successfully
        """
        try:
            # Load report data
            if not Path(report_path).exists():
                self.logger.error(f"❌ Report file not found: {report_path}")
                return False
            
            with open(report_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            # Generate notification content
            title, message, email_content = self._generate_daily_notification(report_data)
            
            # Send via ntfy.sh
            success = self._send_ntfy_notification(title, message, email_content)
            
            if success:
                self.logger.info("✅ Daily report notification sent successfully")
                self.logger.info(f"📱 View at: https://ntfy.sh/{self.ntfy_topic}")
            else:
                self.logger.error("❌ Failed to send daily report notification")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error sending daily report: {e}")
            return False
    
    def send_test_email(self, content: Dict[str, Any]) -> bool:
        """
        Send test notification via ntfy.sh
        
        Args:
            content: Test content
            
        Returns:
            bool: True if sent successfully
        """
        try:
            title = "🧪 Test - Consultancy News Agent"
            message = f"""
Test notification sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

Message: {content.get('message', 'Test message')}

System: Peers Consulting & Technology News Agent
Status: ✅ Working perfectly!

📱 Subscribe to get all reports: https://ntfy.sh/{self.ntfy_topic}
            """.strip()
            
            # Send via ntfy.sh
            success = self._send_ntfy_notification(title, message)
            
            if success:
                self.logger.info("✅ Test notification sent successfully")
                self.logger.info(f"📱 View at: https://ntfy.sh/{self.ntfy_topic}")
            else:
                self.logger.error("❌ Failed to send test notification")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error sending test notification: {e}")
            return False
    
    def send_alert(self, alert_type: str, message: str) -> bool:
        """
        Send alert notification via ntfy.sh
        
        Args:
            alert_type: Type of alert
            message: Alert message
            
        Returns:
            bool: True if sent successfully
        """
        try:
            title = f"🚨 Alert - {alert_type}"
            notification_message = f"""
SYSTEM ALERT

Type: {alert_type}
Message: {message}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

Source: Consultancy News Agent
            """.strip()
            
            # Send via ntfy.sh with high priority
            success = self._send_ntfy_notification(title, notification_message, priority="high")
            
            if success:
                self.logger.info(f"✅ Alert notification sent: {alert_type}")
            else:
                self.logger.error(f"❌ Failed to send alert notification: {alert_type}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error sending alert: {e}")
            return False
    
    def _generate_daily_notification(self, report_data: Dict[str, Any]) -> tuple:
        """Generate daily notification content from report data"""
        
        date = report_data.get('date', 'Unknown')
        total_articles = report_data.get('total_articles', 0)
        high_relevance = report_data.get('high_relevance_articles', 0)
        top_articles = report_data.get('top_articles', [])
        
        title = f"📊 Daily Report - {date}"
        
        # Generate notification message
        message = f"""
📊 DAILY CONSULTANCY NEWS REPORT
Date: {date}

📈 SUMMARY:
• Total Articles: {total_articles}
• High Relevance: {high_relevance}
• Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

🔥 TOP ARTICLES:"""
        
        # Add top 5 articles
        for i, article in enumerate(top_articles[:5], 1):
            title_text = article.get('title', 'No title')
            score = article.get('relevance_score', 0)
            source = article.get('source', 'Unknown')
            
            # Truncate long titles
            if len(title_text) > 60:
                title_text = title_text[:57] + "..."
            
            message += f"\n\n{i}. {title_text}"
            message += f"\n   Score: {score:.1f} | {source}"
        
        if not top_articles:
            message += "\n\nNo high-relevance articles found today."
        
        message += f"\n\n📱 Full report: https://ntfy.sh/{self.ntfy_topic}"
        message += f"\n🏢 Peers Consulting & Technology"
        
        # Generate email content for potential email integration
        email_content = self._generate_email_html(report_data)
        
        return title, message, email_content
    
    def _generate_email_html(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML email content (for future email integration)"""
        
        date = report_data.get('date', 'Unknown')
        total_articles = report_data.get('total_articles', 0)
        high_relevance = report_data.get('high_relevance_articles', 0)
        top_articles = report_data.get('top_articles', [])
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center;">
                <h1>🏢 Peers Consulting & Technology</h1>
                <h2>Daily News Report - {date}</h2>
            </div>
            
            <div style="padding: 20px;">
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
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
                
                html_content += f"""
                <div style="border-left: 4px solid #667eea; padding: 15px; margin: 15px 0; background: #f8f9fa;">
                    <h4 style="margin: 0 0 10px 0;">{i}. <a href="{url}" target="_blank">{title}</a></h4>
                    <div style="color: #666; font-size: 0.9em;">
                        <span style="background: #667eea; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em;">Score: {score:.1f}</span>
                        <strong>Source:</strong> {source}
                    </div>
                </div>
                """
        else:
            html_content += "<p>No high-relevance articles found today.</p>"
        
        # Add footer
        html_content += f"""
            </div>
            
            <div style="text-align: center; color: #666; font-size: 0.9em; margin-top: 30px;">
                <p>📧 Consultancy News Agent | Automated Daily Report</p>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M UTC')}</p>
                <p>📱 Subscribe to notifications: <a href="https://ntfy.sh/{self.ntfy_topic}">https://ntfy.sh/{self.ntfy_topic}</a></p>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _send_ntfy_notification(self, title: str, message: str, email_html: str = None, priority: str = "default") -> bool:
        """
        Send notification via ntfy.sh
        
        Args:
            title: Notification title
            message: Notification message
            email_html: Optional HTML content for email
            priority: Notification priority (min, low, default, high, max)
            
        Returns:
            bool: True if sent successfully
        """
        try:
            headers = {
                'Title': title,
                'Priority': priority,
                'Tags': 'briefcase,chart_with_upwards_trend',
                'Content-Type': 'text/plain; charset=utf-8'
            }
            
            # Add email integration if configured
            webhook_url = os.getenv('EMAIL_WEBHOOK_URL')
            if webhook_url and 'ntfy.sh' not in webhook_url:
                headers['Actions'] = f'view, Open Dashboard, {webhook_url}, clear=true'
            
            # Send notification
            response = requests.post(
                self.ntfy_url,
                data=message.encode('utf-8'),
                headers=headers,
                timeout=30
            )
            
            # Check response
            if response.status_code == 200:
                self.logger.info(f"✅ ntfy.sh notification sent successfully")
                return True
            else:
                self.logger.error(f"❌ ntfy.sh notification failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            self.logger.error("❌ ntfy.sh notification timeout")
            return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ ntfy.sh notification request error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Unexpected ntfy.sh notification error: {e}")
            return False
    
    def is_configured(self) -> bool:
        """Check if ntfy.sh sender is configured (always true)"""
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get ntfy.sh sender status"""
        return {
            'configured': True,
            'service': 'ntfy.sh',
            'topic': self.ntfy_topic,
            'url': f'https://ntfy.sh/{self.ntfy_topic}',
            'recipient': self.recipient_email,
            'type': 'ntfy_push_notification',
            'subscribe_url': f'https://ntfy.sh/{self.ntfy_topic}'
        }
    
    def get_subscription_info(self) -> Dict[str, str]:
        """Get subscription information for the user"""
        return {
            'service': 'ntfy.sh',
            'topic': self.ntfy_topic,
            'web_url': f'https://ntfy.sh/{self.ntfy_topic}',
            'android_app': 'https://play.google.com/store/apps/details?id=io.heckel.ntfy',
            'ios_app': 'https://apps.apple.com/us/app/ntfy/id1625396347',
            'instructions': f'1. Install ntfy app or visit https://ntfy.sh/{self.ntfy_topic}\n2. Subscribe to topic: {self.ntfy_topic}\n3. Receive instant notifications!'
        }

