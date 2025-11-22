{
    'name': 'Stock Restriction on Sales Orders',
    'version': '1.0',
    'author': 'Your Name',
    'category': 'Sales',
    'license': 'LGPL-3',
    'summary': 'Restricts order confirmation and invoicing if products are out of stock.',
    'depends': ['sale', 'stock'],
    'data': [
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
