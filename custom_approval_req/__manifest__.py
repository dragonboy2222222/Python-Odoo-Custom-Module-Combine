{
    'name': 'Approval Request Customization2',
    'version': '1.0',
    'category': 'Customization',
    'summary': 'Adds areas and departments to approval requests.',
    'description': """
        - Add Areas as a new model
        - Link Areas and Departments to Users
        - Enhance Approval Requests with Department and Area fields
    """,
    'author': 'Thein Paing Htun',
    'depends': ['base', 'sale','hr','mail','product'],
    'data': [
        'secrutiy/security.xml',
        'secrutiy/ir.model.access.csv',
        'views/res_area.xml',
        'views/res_user.xml',
        'views/approval view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
