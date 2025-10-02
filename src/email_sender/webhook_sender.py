"""
Real SMTP Email System using Gmail
Direct email delivery to heitor.a.marin@gmail.com
"""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from ..utils.logger import get_logger

class WebhookEmailSender:
    """
    Real SMTP email sender using Gmail
    Sends actual emails to heitor.a.marin@gmail.com
    """
    
    def __init__(self):
        """Initialize Gmail SMTP email sender"""
        self.logger = get_logger("gmail_smtp")
        
        # Gmail SMTP configuration
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv('GMAIL_EMAIL', 'heitor.a.marin@gmail.com')
        self.sender_password = os.getenv('GMAIL_APP_PASSWORD')
        self.recipient_email = "heitor.a.marin@gmail.com"
        
        # Check configuration
        if self.sender_password:
            self.logger.info("✅ Gmail SMTP configured successfully")
            self.logger.info(f"📧 Sender: {self.sender_email}")
            self.logger.info(f"📧 Recipient: {self.recipient_email}")
        else:
            self.logger.error("❌ GMAIL_APP_PASSWORD not configured")
    
    def send_daily_report(self, report_path: str) -> bool:
        """
        Send daily report via Gmail SMTP
        
        Args:
            report_path: Path to the JSON report file
            
        Returns:
            bool: True if sent successfully
        """
        try:
            if not self.sender_password:
                self.logger.error("❌ Gmail credentials not configured")
                return False
            
            # Load report data
            if not Path(report_path).exists():
                self.logger.error(f"❌ Report file not found: {report_path}")
                return False
            
            with open(report_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            # Generate email content
            subject, html_content, text_content = self._generate_daily_email_content(report_data)
            
            # Send via Gmail SMTP
            success = self._send_gmail_email(subject, html_content, text_content)
            
            if success:
                self.logger.info("✅ Daily report email sent successfully via Gmail")
            else:
                self.logger.error("❌ Failed to send daily report email")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error sending daily report: {e}")
            return False
    
    def send_test_email(self, content: Dict[str, Any]) -> bool:
        """
        Send test email via Gmail SMTP
        
        Args:
            content: Test email content
            
        Returns:
            bool: True if sent successfully
        """
        try:
            if not self.sender_password:
                self.logger.error("❌ Gmail credentials not configured")
                return False
            
            subject = "🧪 Test Email - Consultancy News Agent"
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 8px; }}
                    .content {{ padding: 20px; }}
                    .success {{ background: #d4edda; color: #155724; padding: 15px; border-radius: 8px; margin: 15px 0; }}
                    .footer {{ text-align: center; color: #666; font-size: 0.9em; margin-top: 30px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🏢 Peers Consulting & Technology</h1>
                    <h2>🧪 Test Email - System Working!</h2>
                </div>
                
                <div class="content">
                    <div class="success">
                        <h3>✅ SUCCESS! Email system is working perfectly!</h3>
                        <p><strong>Message:</strong> {content.get('message', 'Gmail SMTP test successful')}</p>
                        <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                        <p><strong>System:</strong> Consultancy News Agent</p>
                        <p><strong>Method:</strong> Gmail SMTP Direct</p>
                    </div>
                    
                    <h3>📊 System Status:</h3>
                    <ul>
                        <li>✅ <strong>Gmail SMTP:</strong> Connected and working</li>
                        <li>✅ <strong>Railway:</strong> Deployed and running</li>
                        <li>✅ <strong>GitHub Actions:</strong> Automated daily collection</li>
                        <li>✅ <strong>Email Delivery:</strong> Direct to Gmail inbox</li>
                    </ul>
                    
                    <h3>📅 Next Steps:</h3>
                    <p>You will now receive daily consultancy news reports automatically at 8:00 UTC every day.</p>
                </div>
                
                <div class="footer">
                    <p>📧 Consultancy News Agent | Test Email Confirmation</p>
                    <p>Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M UTC')}</p>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            🏢 PEERS CONSULTING & TECHNOLOGY
            🧪 Test Email - System Working!
            
            ✅ SUCCESS! Email system is working perfectly!
            
            Message: {content.get('message', 'Gmail SMTP test successful')}
            Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
            System: Consultancy News Agent
            Method: Gmail SMTP Direct
            
            📊 SYSTEM STATUS:
            ✅ Gmail SMTP: Connected and working
            ✅ Railway: Deployed and running  
            ✅ GitHub Actions: Automated daily collection
            ✅ Email Delivery: Direct to Gmail inbox
            
            📅 NEXT STEPS:
            You will now receive daily consultancy news reports automatically at 8:00 UTC every day.
            
            📧 Consultancy News Agent | Test Email Confirmation
            Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M UTC')}
            """
            
            # Send via Gmail SMTP
            success = self._send_gmail_email(subject, html_content, text_content)
            
            if success:
                self.logger.info("✅ Test email sent successfully via Gmail")
            else:
                self.logger.error("❌ Failed to send test email")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error sending test email: {e}")
            return False
    
    def send_alert(self, alert_type: str, message: str) -> bool:
        """
        Send alert email via Gmail SMTP
        
        Args:
            alert_type: Type of alert
            message: Alert message
            
        Returns:
            bool: True if sent successfully
        """
        try:
            if not self.sender_password:
                self.logger.error("❌ Gmail credentials not configured")
                return False
            
            subject = f'🚨 Alert - {alert_type} - Peers Consulting & Technology'
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="background: #dc3545; color: white; padding: 20px; text-align: center; border-radius: 8px;">
                    <h1>🚨 System Alert</h1>
                </div>
                
                <div style="padding: 20px;">
                    <div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 8px; margin: 15px 0;">
                        <h3>Alert Details:</h3>
                        <p><strong>Type:</strong> {alert_type}</p>
                        <p><strong>Message:</strong> {message}</p>
                        <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                    </div>
                </div>
                
                <div style="text-align: center; color: #666; font-size: 0.9em; margin-top: 30px;">
                    <p>📧 Consultancy News Agent | Automated Alert</p>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            🚨 SYSTEM ALERT
            
            Type: {alert_type}
            Message: {message}
            Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
            
            📧 Consultancy News Agent | Automated Alert
            """
            
            # Send via Gmail SMTP
            success = self._send_gmail_email(subject, html_content, text_content)
            
            if success:
                self.logger.info(f"✅ Alert email sent: {alert_type}")
            else:
                self.logger.error(f"❌ Failed to send alert email: {alert_type}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error sending alert: {e}")
            return False
    
    def _send_gmail_email(self, subject: str, html_content: str, text_content: str) -> bool:
        """
        Send email via Gmail SMTP
        
        Args:
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text email content
            
        Returns:
            bool: True if sent successfully
        """
        try:
            if not self.sender_password:
                self.logger.error("❌ Gmail app password not configured")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            
            # Add text and HTML parts
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Connect to Gmail SMTP server
            self.logger.info(f"📧 Connecting to Gmail SMTP server...")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            
            # Login with app password
            self.logger.info(f"🔐 Authenticating with Gmail...")
            server.login(self.sender_email, self.sender_password)
            
            # Send email
            self.logger.info(f"📤 Sending email to {self.recipient_email}...")
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"✅ Email sent successfully via Gmail SMTP")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            self.logger.error(f"❌ Gmail authentication failed: {e}")
            self.logger.error("💡 Check if app password is correct and 2FA is enabled")
            return False
        except smtplib.SMTPException as e:
            self.logger.error(f"❌ SMTP error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Unexpected error sending email: {e}")
            return False
    
    def _generate_daily_email_content(self, report_data: Dict[str, Any]) -> tuple:
        """Generate daily email content from report data"""
        
        date = report_data.get('date', 'Unknown')
        total_articles = report_data.get('total_articles', 0)
        high_relevance = report_data.get('high_relevance_articles', 0)
        top_articles = report_data.get('top_articles', [])
        
        subject = f"📊 Daily Consultancy Report - {date} ({high_relevance} high-relevance articles)"
        
        # Generate HTML content
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 8px; }}
                .content {{ padding: 20px; }}
                .stats {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .article {{ border-left: 4px solid #667eea; padding: 15px; margin: 15px 0; background: #f8f9fa; border-radius: 4px; }}
                .article h3 {{ margin: 0 0 10px 0; color: #333; }}
                .article .meta {{ color: #666; font-size: 0.9em; margin: 5px 0; }}
                .article .score {{ background: #667eea; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; }}
                .footer {{ text-align: center; color: #666; font-size: 0.9em; margin-top: 30px; }}
                .no-articles {{ background: #fff3cd; color: #856404; padding: 15px; border-radius: 8px; margin: 15px 0; }}
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
                    <h3>{i}. <a href="{url}" target="_blank" style="color: #667eea; text-decoration: none;">{title}</a></h3>
                    <div class="meta">
                        <span class="score">Score: {score:.1f}</span>
                        <strong>Source:</strong> {source} | 
                        <strong>Category:</strong> {category}
                        {f' | <strong>Firms:</strong> {firms}' if firms else ''}
                    </div>
                </div>
                """
        else:
            html_content += '<div class="no-articles"><p>No high-relevance articles found today. The system will continue monitoring for relevant consultancy news.</p></div>'
        
        # Add footer
        html_content += f"""
            </div>
            
            <div class="footer">
                <p>📧 Consultancy News Agent | Automated Daily Report</p>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M UTC')}</p>
                <p>🔄 Next report will be sent tomorrow at 8:00 UTC</p>
            </div>
        </body>
        </html>
        """
        
        # Generate text version
        text_content = f"""
        🏢 PEERS CONSULTING & TECHNOLOGY
        Daily News Report - {date}
        
        📊 DAILY SUMMARY:
        • Total Articles: {total_articles}
        • High Relevance: {high_relevance}
        • Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
        
        🔥 TOP ARTICLES:
        """
        
        if top_articles:
            for i, article in enumerate(top_articles[:5], 1):
                title = article.get('title', 'No title')
                url = article.get('url', '#')
                score = article.get('relevance_score', 0)
                source = article.get('source', 'Unknown')
                text_content += f"\n{i}. {title}\n   Score: {score:.1f} | Source: {source}\n   URL: {url}\n"
        else:
            text_content += "\nNo high-relevance articles found today.\nThe system will continue monitoring for relevant consultancy news.\n"
        
        text_content += f"""
        
        📧 Consultancy News Agent | Automated Daily Report
        Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M UTC')}
        🔄 Next report will be sent tomorrow at 8:00 UTC
        """
        
        return subject, html_content, text_content
    
    def is_configured(self) -> bool:
        """Check if Gmail SMTP is configured"""
        return bool(self.sender_password)
    
    def get_status(self) -> Dict[str, Any]:
        """Get Gmail SMTP sender status"""
        return {
            'configured': self.is_configured(),
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'sender_email': self.sender_email,
            'recipient_email': self.recipient_email,
            'type': 'gmail_smtp_direct'
        }

