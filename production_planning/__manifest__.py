# -*- coding: utf-8 -*-
{
    'name': 'Production Planning',
    'version': '17.0.0.0',
    'summary': 'To manage production planning reports.',
    'description': """To manage production planning reports.""",
    'author': ['Hetvi Jesadiya', 'Mansi Vaghela'],
    'category': 'sale',
    'website': 'www.teknovatesolution.com',
    'depends': ['sale', 'mrp'],
    'data': [
        'views/sale_order.xml',
        'views/sale_order_line.xml',
        'views/mrp_production_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'production_planning/static/src/js/binary_field_preview.xml',
            'production_planning/static/src/js/binary_field_preview.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
