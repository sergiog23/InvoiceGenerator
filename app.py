"""
Flask App - Webhook endpoint for Twilio SMS
"""

from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from invoice_parser import InvoiceParser
from pdf_filler import InvoiceFiller
from email_sender import EmailSender
from pathlib import Path
import os
import tempfile
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TEMPLATE_PATH = os.getenv('TEMPLATE_PATH', 'BASE_INVOICE.pdf')


@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'Guerrero\'s Electric Invoice Generator',
        'version': '1.0'
    })


@app.route('/webhook/sms', methods=['POST'])
def sms_webhook():
    """
    Twilio SMS webhook endpoint
    Receives SMS, generates invoice, emails it
    """
    try:
        # Get message from Twilio
        message_body = request.form.get('Body', '')
        from_number = request.form.get('From', '')
        
        logger.info(f"Received SMS from {from_number}")
        logger.info(f"Message: {message_body[:100]}...")
        
        # Parse the invoice data
        parser = InvoiceParser(message_body)
        invoice_data = parser.parse()
        
        logger.info(f"Parsed invoice #{invoice_data.get('invoice_number', 'N/A')}")
        
        # Generate PDF
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / f"invoice_{invoice_data['invoice_number']}.pdf"
            
            filler = InvoiceFiller(TEMPLATE_PATH)
            success = filler.fill(invoice_data, str(output_path))
            
            if not success:
                raise Exception("Failed to fill PDF")
            
            logger.info("PDF generated successfully")
            
            # Send email
            email_sender = EmailSender()
            email_sent = email_sender.send_invoice(str(output_path), invoice_data)
            
            if not email_sent:
                raise Exception("Failed to send email")
            
            logger.info("Email sent successfully")
        
        # Respond to SMS
        resp = MessagingResponse()
        resp.message(
            f"✅ Invoice #{invoice_data['invoice_number']} generated and sent to your email!"
        )
        
        return str(resp)
        
    except Exception as e:
        logger.error(f"Error processing SMS: {e}")
        
        # Send error response
        resp = MessagingResponse()
        resp.message(
            f"❌ Error generating invoice: {str(e)}\n\n"
            "Please check the message format and try again."
        )
        
        return str(resp)


@app.route('/webhook/test', methods=['POST'])
def test_webhook():
    """
    Test endpoint - doesn't require Twilio
    Useful for testing locally
    """
    try:
        data = request.get_json()
        message_body = data.get('message', '')
        
        if not message_body:
            return jsonify({'error': 'No message provided'}), 400
        
        # Parse the invoice data
        parser = InvoiceParser(message_body)
        invoice_data = parser.parse()
        
        # Generate PDF
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / f"invoice_{invoice_data['invoice_number']}.pdf"
            
            filler = InvoiceFiller(TEMPLATE_PATH)
            success = filler.fill(invoice_data, str(output_path))
            
            if not success:
                return jsonify({'error': 'Failed to fill PDF'}), 500
            
            # Send email
            email_sender = EmailSender()
            email_sent = email_sender.send_invoice(str(output_path), invoice_data)
            
            if not email_sent:
                return jsonify({'error': 'Failed to send email'}), 500
        
        return jsonify({
            'success': True,
            'invoice_number': invoice_data['invoice_number'],
            'customer': invoice_data['customer_name']
        })
        
    except Exception as e:
        logger.error(f"Error in test endpoint: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

### **File 6: `Procfile`** (For Railway)
```
web: gunicorn app:app
```

### **File 7: `runtime.txt`** (Optional - specify Python version)
```
python-3.11.0