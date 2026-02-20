"""
Invoice Parser - Extracts data from text messages
"""

import re
from datetime import datetime


class InvoiceParser:
    """Parses text message format into invoice data"""
    
    def __init__(self, text):
        self.text = text.strip()
        self.data = {
            'invoice_number': '',
            'date': '',
            'customer_name': '',
            'customer_address': '',
            'customer_city_state_zip': '',
            'job_description': '',
            'line_items': [],
            'total': 0.0
        }
    
    def parse(self):
        """Parse the text and extract invoice information"""
        lines = self.text.split('\n')
        current_section = None
        line_items = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Customer name
            if re.match(r'^(customer|name|to):\s*', line, re.IGNORECASE):
                self.data['customer_name'] = re.sub(
                    r'^(customer|name|to):\s*', '', line, flags=re.IGNORECASE
                ).strip()
            
            # Address
            elif re.match(r'^address:\s*', line, re.IGNORECASE):
                address = re.sub(r'^address:\s*', '', line, flags=re.IGNORECASE).strip()
                self.data['customer_address'] = address
            
            # Job description
            elif re.match(r'^(job|for|service):\s*', line, re.IGNORECASE):
                self.data['job_description'] = re.sub(
                    r'^(job|for|service):\s*', '', line, flags=re.IGNORECASE
                ).strip()
            
            # Invoice number
            elif re.match(r'^(invoice|invoice #|inv|#):\s*', line, re.IGNORECASE):
                self.data['invoice_number'] = re.sub(
                    r'^(invoice|invoice #|inv|#):\s*', '', line, flags=re.IGNORECASE
                ).strip()
            
            # Date
            elif re.match(r'^date:\s*', line, re.IGNORECASE):
                self.data['date'] = re.sub(
                    r'^date:\s*', '', line, flags=re.IGNORECASE
                ).strip()
            
            # Total
            elif re.match(r'^total:\s*', line, re.IGNORECASE):
                total_text = re.sub(r'^total:\s*', '', line, flags=re.IGNORECASE).strip()
                total_match = re.search(r'[\d,]+\.?\d*', total_text.replace('$', ''))
                if total_match:
                    self.data['total'] = float(total_match.group().replace(',', ''))
            
            # Line items section
            elif re.match(r'^(line items|items|work done|services):\s*$', line, re.IGNORECASE):
                current_section = 'line_items'
            
            # Parse line items
            elif current_section == 'line_items':
                if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                    item_text = line[1:].strip()
                else:
                    item_text = line
                
                # Extract price if present
                price_match = re.search(r'[-–—]\s*\$?\s*([\d,]+\.?\d*)\s*$', item_text)
                if price_match:
                    description = item_text[:price_match.start()].strip()
                    amount = price_match.group(1).replace(',', '')
                else:
                    description = item_text
                    amount = ''
                
                if description and not re.match(r'^total', description, re.IGNORECASE):
                    line_items.append({
                        'description': description,
                        'amount': amount
                    })
        
        self.data['line_items'] = line_items
        
        # Auto-generate date if not provided
        if not self.data['date']:
            self.data['date'] = datetime.now().strftime('%m/%d/%Y')
        
        # Split address
        if self.data['customer_address']:
            self._split_address()
        
        return self.data
    
    def _split_address(self):
        """Split address into street and city/state/zip"""
        address = self.data['customer_address']
        parts = address.split(',')
        
        if len(parts) >= 2:
            self.data['customer_address'] = parts[0].strip()
            self.data['customer_city_state_zip'] = ','.join(parts[1:]).strip()