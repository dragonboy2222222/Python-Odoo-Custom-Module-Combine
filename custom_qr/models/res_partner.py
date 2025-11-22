# customer_qr_code/models/warehouse.py
from odoo import models, fields, api
import base64
import qrcode
from io import BytesIO

class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_qr_code = fields.Binary("Customer QR Code", attachment=True)

    def generate_qr_code(self):
        for record in self:
            # Generate QR code content with formatted customer data
            qr_data = f"""
            Name: {record.name or 'N/A'}
            Email: {record.email or 'N/A'}
            Phone: {record.phone or 'N/A'}
            """
            # Generate the QR code image
            qr_img = qrcode.make(qr_data)
            buffer = BytesIO()
            qr_img.save(buffer, format="PNG")
            qr_code_image = base64.b64encode(buffer.getvalue())
            record.customer_qr_code = qr_code_image
