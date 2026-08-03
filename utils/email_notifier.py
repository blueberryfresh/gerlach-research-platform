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

INVESTIGATOR_EMAILS = ["kchoi29@gmu.edu", "il.im@yonsei.ac.kr"]

# gerlach_type and assigned_personality are both stored as these snake_case keys
# (see agents/big5_assessment_agent.py classify_gerlach_type) — map to display labels
# for the notification email. Coincidentally the same 4 keys are reused for the AI's
# assigned conversational personality; they are independent taxonomies.
GERLACH_DISPLAY = {
    "average": "Average",
    "role_model": "Role Model",
    "self_centred": "Self-Centred",
    "reserved": "Reserved",
}
TASK_DISPLAY = {
    "NOBLE INDUSTRIES for Big5.pdf": "Noble Industries",
    "Popcorn Brain Task for Big5-rev2.pdf": "Popcorn Brain",
}


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

    @staticmethod
    def _crosstab_table_html(title: str, crosstab: dict, columns: list, column_display: dict) -> str:
        """Render a Gerlach-type x <columns> balance table (e.g. type x task, or
        type x AI personality) as an HTML table for the notification email."""
        header_cells = "".join(f"<th>{column_display.get(c, c)}</th>" for c in columns)
        rows_html = ""
        for gtype in ["average", "role_model", "self_centred", "reserved"]:
            row_counts = crosstab.get(gtype, {})
            cells = "".join(f"<td>{row_counts.get(c, 0)}</td>" for c in columns)
            rows_html += f"<tr><td><strong>{GERLACH_DISPLAY.get(gtype, gtype)}</strong></td>{cells}</tr>"
        return f"""
        <h4 style="margin-bottom:4px;">{title}</h4>
        <table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse;">
            <tr><th>Gerlach Type</th>{header_cells}</tr>
            {rows_html}
        </table>
        """

    def send_completion_notification(
        self,
        user_id: str,
        session_id: str,
        gerlach_type: str = None,
        assigned_task: str = None,
        assigned_personality: str = None,
        consent_withdrawn: bool = False,
        type_counts: dict = None,
        task_crosstab: dict = None,
        personality_crosstab: dict = None,
    ) -> bool:
        """
        Send email notification when participant completes study.

        Includes this participant's Gerlach type, assigned task, and assigned AI
        personality, plus the current study-wide balance across all three (as of
        the moment this participant completed), so investigators can monitor
        recruitment balance from the email itself without logging into the admin
        dashboard.

        Args:
            user_id: Participant ID
            session_id: Session ID
            gerlach_type: This participant's classified Gerlach type (raw snake_case key)
            assigned_task: This participant's assigned task (raw filename)
            assigned_personality: This participant's assigned AI personality (raw snake_case key)
            consent_withdrawn: Whether the participant withdrew data consent at re-consent
            type_counts: {gerlach_type: count} across all participants so far
            task_crosstab: {gerlach_type: {task: count}} across all participants so far
            personality_crosstab: {gerlach_type: {ai_personality: count}} across all participants so far

        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.is_configured():
            self.logger.warning("Email not configured. Skipping notification.")
            return False

        try:
            subject = f"Participant Completed Study: {user_id}"

            gerlach_display = GERLACH_DISPLAY.get(gerlach_type, gerlach_type or "Unknown")
            task_display = TASK_DISPLAY.get(assigned_task, assigned_task or "Unknown")
            personality_display = GERLACH_DISPLAY.get(assigned_personality, assigned_personality or "Unknown")
            consent_line = (
                "<li><strong>⚠️ Data consent withdrawn at re-consent step</strong></li>"
                if consent_withdrawn else ""
            )

            type_counts_html = ""
            if type_counts:
                rows = "".join(
                    f"<tr><td>{GERLACH_DISPLAY.get(t, t)}</td><td>{c}</td></tr>"
                    for t, c in type_counts.items()
                )
                type_counts_html = f"""
                <h4 style="margin-bottom:4px;">Participants per Personality Type</h4>
                <table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse;">
                    <tr><th>Gerlach Type</th><th>Count</th></tr>
                    {rows}
                </table>
                """

            task_table_html = ""
            if task_crosstab:
                task_table_html = self._crosstab_table_html(
                    "Personality Type × Task", task_crosstab,
                    list(TASK_DISPLAY.keys()), TASK_DISPLAY,
                )

            personality_table_html = ""
            if personality_crosstab:
                personality_table_html = self._crosstab_table_html(
                    "Personality Type × AI Personality", personality_crosstab,
                    list(GERLACH_DISPLAY.keys()), GERLACH_DISPLAY,
                )

            body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                             color: white; padding: 20px; border-radius: 5px; }}
                    .content {{ padding: 20px; }}
                    .details {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                    table {{ margin: 6px 0 16px 0; font-size: 0.9em; }}
                    th {{ background: #eee; }}
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
                            <li><strong>Gerlach Personality Type:</strong> {gerlach_display}</li>
                            <li><strong>Assigned Task:</strong> {task_display}</li>
                            <li><strong>Assigned AI Personality:</strong> {personality_display}</li>
                            {consent_line}
                        </ul>
                    </div>

                    <div class="details">
                        <h3>Current Study Balance (all participants, as of this completion)</h3>
                        {type_counts_html}
                        {task_table_html}
                        {personality_table_html}
                        <p style="font-size:0.85em;color:#666;">
                            For the live, always-current view, see the admin dashboard's
                            "Personality Type &amp; Task Assignment" section.
                        </p>
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
