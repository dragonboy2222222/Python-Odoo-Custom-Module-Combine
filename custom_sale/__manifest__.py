{
    'name': 'Custom Sale Order',
    'version': '1.0',
    'category': 'Sales',
    'description': 'Custom Sales Order model with additional delivery types.',
    'depends': ['sale', 'account'],
    'data': [

        'views/invoice.xml',
        'views/account.xml'

    ],
    'installable': True,
    'application': False,
}
