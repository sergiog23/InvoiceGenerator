"""
PDF Filler - Fills invoice template with data
"""

from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter


class InvoiceFiller:
    """Fills PDF invoice template with parsed data"""
    
    def __init__(self, template_path):
        self.template_path = Path(template_path)
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        self.pdf_fields = self._get_pdf_fields()
    
    def _get_pdf_fields(self):
        """Get list of field names from the PDF"""
        reader = PdfReader(str(self.template_path))
        fields = reader.get_fields()
        return list(fields.keys()) if fields else []
    
    def fill(self, data, output_path):
        """Fill the PDF with invoice data"""
        reader = PdfReader(str(self.template_path))
        writer = PdfWriter()
        
        if not reader.get_fields():
            print("⚠ WARNING: No form fields found in PDF template!")
            return False
        
        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)
        
        # Map data to fields
        field_data = self._smart_map_fields(data)
        
        # Fill the form
        try:
            writer.update_page_form_field_values(
                writer.pages[0],
                field_data
            )
        except Exception as e:
            print(f"⚠ Error filling fields: {e}")
            return False
        
        # Write output
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return True
    
    def _smart_map_fields(self, data):
        """Intelligently map data to PDF fields based on field names"""
        field_map = {}
        
        for pdf_field in self.pdf_fields:
            field_lower = pdf_field.lower()
            
            # Invoice Number
            if any(x in field_lower for x in ['invoice', 'inv #', 'inv#', 'number']):
                if 'date' not in field_lower:
                    field_map[pdf_field] = data['invoice_number']
            
            # Date
            elif 'date' in field_lower:
                field_map[pdf_field] = data['date']
            
            # Customer Name / TO
            elif any(x in field_lower for x in ['to', 'customer', 'name', 'client']):
                if 'address' not in field_lower:
                    customer_info = data['customer_name']
                    if data['customer_address']:
                        customer_info += '\n' + data['customer_address']
                    if data['customer_city_state_zip']:
                        customer_info += '\n' + data['customer_city_state_zip']
                    field_map[pdf_field] = customer_info
            
            # Job Description / FOR
            elif any(x in field_lower for x in ['for', 'service', 'job', 'project']):
                field_map[pdf_field] = data['job_description']
            
            # Description / Line Items
            elif any(x in field_lower for x in ['description', 'item', 'work']):
                if 'amount' not in field_lower:
                    descriptions = []
                    for item in data['line_items']:
                        descriptions.append(item['description'])
                    field_map[pdf_field] = '\n'.join(descriptions)
            
            # Amount / Total
            elif any(x in field_lower for x in ['amount', 'total', 'price']):
                if data['total'] > 0:
                    field_map[pdf_field] = f"${data['total']:,.2f}"
                elif 'amount' in field_lower and data['line_items']:
                    amounts = []
                    for item in data['line_items']:
                        if item['amount']:
                            amounts.append(f"${item['amount']}")
                        else:
                            amounts.append('')
                    field_map[pdf_field] = '\n'.join(amounts)
        
        return field_map