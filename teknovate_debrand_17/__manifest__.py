# -*- coding: utf-8 -*-
{
    'name' : 'Teknovative Solution Debrand 17',
    'version' : '17.0.0.1',
    'summary': 'Teknovative Solution',
    'author' : 'Sona Solani',
    'description': """Teknovative Solution""",
    'category': 'Teknovative Solution',
    'website': 'https://teknovativesolution.com/',
    'depends' : [
        # 'base','crm','app_odoo_customize','web'
        'base', 'web', 'mail'
    ],
    'data': [
             'views/mailbot_data.xml',
             'views/res_partner.xml',
             'views/webclient_templates.xml',
            ],
    'assets': {
            'web.assets_backend': [
                'teknovate_debrand_17/static/src/js/remove_odoo_account_item.js',
            ],
        },
    'installable': True,
    'application': True,
    'auto_install': False,
}
