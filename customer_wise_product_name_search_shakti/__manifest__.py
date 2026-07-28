# -*- coding: utf-8 -*-

{
    'name': 'Customer wise product name search Shakti',
    'version': '17.0.0.0',
    'category': 'Sales',
    'author': 'Hardik Chauhan',
    'description': """To search product from customerwise.""",
    'summary': 'To search product from customerwise.',
    'website': 'http://www.teknovativesolution.com/',
    'images': [],
    'depends': ['sale','sales_team','sale_management'],
    'data': [
            'security/ir.model.access.csv',
            'views/product_customerinfo.xml',
            'views/product_template.xml',
            'views/product_name.xml',
            'views/product_code.xml',
            'views/sale_order.xml'

            ],
    'qweb' :[],
    'installable': True,
    'application': True,
    'auto_install': False,
}
