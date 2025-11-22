# customer_qr_code/__manifest__.py
{
    'name': "Custom Cancel Sale",
    'version': '1.0',
    'depends': ['base', 'sale'],
    'author': "Thein Paing Htun",
    'category': 'Custom',
    'summary': "Cancel Reason For Sale Order Cancellation",
    'description': """
      This module is for Canceling Order In Sale Order Module
    """,
    'data': [
        'views/dialogbox.xml'


    ],
}
