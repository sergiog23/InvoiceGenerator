"""
Email Sender - Sends generated invoices via email
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
import os


class EmailSender:
    """Send emails with PDF attachments"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_address = os.getenv('EMAIL_ADDRESS')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')
        
        if not all([self.email_address, self.email_password, self.recipient_email]):
            raise ValueError("Email configuration missing in environment variables")
    
    def send_invoice(self, pdf_path, invoice_data):
        """Send invoice PDF via email"""
        msg = MIMEMultipart()
        msg['From'] = self.email_address
        msg['To'] = self.recipient_email
        msg['Subject'] = f"New Invoice Generated - #{invoice_data.get('invoice_number', 'N/A')}"
        
        # Email body
        body = f"""
New invoice has been generated!

Customer: {invoice_data.get('customer_name', 'N/A')}
Invoice #: {invoice_data.get('invoice_number', 'N/A')}
Date: {invoice_data.get('date', 'N/A')}
Job: {invoice_data.get('job_description', 'N/A')}
Total: ${invoice_data.get('total', 0):,.2f}

Line Items:
"""
        for item in invoice_data.get('line_items', []):
            amount_str = f" - ${item['amount']}" if item['amount'] else ""
            body += f"  • {item['description']}{amount_str}\n"
        
        body += "\n\nInvoice PDF is attached."
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach PDF
        pdf_path = Path(pdf_path)
        if pdf_path.exists():
            with open(pdf_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {pdf_path.name}'
                )
                msg.attach(part)
        
        # Send email
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False