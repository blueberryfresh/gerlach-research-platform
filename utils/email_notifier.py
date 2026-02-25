"""
Email Notification Utility for Participant Completion
Sends automated emails to investigators when participants complete the study
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
import os

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

INVESTIGATOR_EMAILS = ["forgeai1004@gmail.com", "il.im@yonsei.ac.kr"]

class EmailNotifier:
    """Handles email notifications for study completion"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.smtp_server = self._get_config("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(self._get_config("SMTP_PORT", "587"))
        self.sender_email = self._get_config("SENDER_EMAIL", "")
        self.sender_password = self._get_config("SENDER_PASSWORD", "")
    
    def _get_config(self, key: str, default: str = "") -> str:
        """Get configuration from Streamlit secrets or environment"""
        if HAS_STREAMLIT and hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
        return os.environ.get(key, default)
    
    def is_configured(self) -> bool:
        """Check if email is properly configured"""
        return bool(self.sender_email and self.sender_password)
    
    def send_completion_notification(self, user_id: str, session_id: str) -> bool:
        """
        Send email notification when participant completes study
        
        Args:
            user_id: Participant ID
            session_id: Session ID
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.is_configured():
            self.logger.warning("Email not configured. Skipping notification.")
            return False
        
        try:
            subject = f"Participant Completed Study: {user_id}"
            
            body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                             color: white; padding: 20px; border-radius: 5px; }}
                    .content {{ padding: 20px; }}
                    .details {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                    .footer {{ color: #666; font-size: 0.9em; margin-top: 30px; padding-top: 20px; 
                             border-top: 1px solid #ddd; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>🎉 Participant Study Completion Notification</h2>
                </div>
                
                <div class="content">
                    <p>A participant has successfully completed the Gerlach Research Platform study.</p>
                    
                    <div class="details">
                        <h3>Participant Details:</h3>
                        <ul>
                            <li><strong>Participant ID:</strong> {user_id}</li>
                            <li><strong>Session ID:</strong> {session_id}</li>
                            <li><strong>Completion Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</li>
                        </ul>
                    </div>
                    
                    <p><strong>Next Steps:</strong></p>
                    <ol>
                        <li>Log in to the admin dashboard to download the participant's data</li>
                        <li>Review the participant's summary report</li>
                        <li>Export data for analysis if needed</li>
                    </ol>
                    
                    <p>The participant's complete data package includes:</p>
                    <ul>
                        <li>Big5 personality assessment results</li>
                        <li>Complete dialogue transcript</li>
                        <li>Task-specific responses</li>
                        <li>Post-experiment survey responses</li>
                        <li>Comprehensive summary report (Markdown & HTML)</li>
                    </ul>
                </div>
                
                <div class="footer">
                    <p>This is an automated notification from the Gerlach Research Platform.</p>
                    <p>For questions or issues, please check the admin dashboard or contact technical support.</p>
                </div>
            </body>
            </html>
            """
            
            for recipient_email in INVESTIGATOR_EMAILS:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = self.sender_email
                msg['To'] = recipient_email
                
                html_part = MIMEText(body, 'html')
                msg.attach(html_part)
                
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.sender_email, self.sender_password)
                    server.send_message(msg)
                
                self.logger.info(f"Completion email sent to {recipient_email} for participant {user_id}")
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error sending completion email: {e}")
            return False
    
    def send_test_email(self, test_user_id: str = "TEST_001") -> bool:
        """Send a test email to verify configuration"""
        return self.send_completion_notification(test_user_id, "test_session_123")
