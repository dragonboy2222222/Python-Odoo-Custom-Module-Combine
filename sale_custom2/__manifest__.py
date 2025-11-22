{
    'name': 'Sale Order Fixed Discount',
    'version': '1.0',
    'summary': 'Adds a fixed discount field to sales and invoice order lines',
    'depends': ['sale', 'account'],
    'data': [
        'views/sale_order_fixed_discount_view.xml',
    ],
    'installable': True,
    'application': False,
}
