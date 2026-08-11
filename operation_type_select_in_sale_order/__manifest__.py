{
    'name': 'Sale Order - Deliver To Location',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Add delivery location selection in Sale Orders based on picking type',
    'description': """
         This module adds a 'Deliver From' field in Sale Order form
        that shows delivery locations based on warehouse.
    """,
    'author': 'Geeta Thummar',
    'website': 'https://www.teknovativesolution.com/',
    'depends': ['sale_stock', 'stock'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}