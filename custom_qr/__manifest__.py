# customer_qr_code/__manifest__.py
{
    'name': "Customer QR Code",
    'version': '1.0',
    'depends': ['base'],
    'author': "Your Name",
    'category': 'Custom',
    'summary': "Generates QR codes for customer information",
    'description': """
        This module adds a QR code field to customer records in Odoo, containing customer information such as name, email, and phone.
    """,
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
    ],
}
