# -*- encoding: utf-8 -*-

{
    'name': 'MO Lot pass from RM to FG 17',
    'version': '17.0.0.1',
    'category': 'manufacturing',
    'summary': """Lot no passed from Raw material to Finished Good Lot in Mrp Production.""",
    'depends': ['base','mrp','stock'],
    'author':'Sona Solani',
    'data': [
         'views/mrp_production.xml',
        'views/product_category.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
