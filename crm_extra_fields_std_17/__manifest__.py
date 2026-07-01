# -*- coding: utf-8 -*-

{
    'name': 'CRM Extra Fields Std 17',
    'version': '17.0.0.1',
    'category': 'sale',
    'author': 'Sona Solani',
    'description': """mobile and email alternative fields""",
    'summary': 'mobile and email alternative fields',
    'website': 'http://www.teknovativesolution.com/',
    'images': [],
    # 'depends': ['base', 'crm', 'account'],
    'depends': ['base', 'crm'],
    'data': [
            'security/ir.model.access.csv',
            'data/customer_type_data.xml',
            'views/crm_lead.xml',
            'views/res_partner.xml',
            ],
    'qweb' :[],
    'assets': {
        'web.assets_backend': [
            'crm_extra_fields_std_17/static/src/css/view.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
