# -*- coding: utf-8 -*-
{
    'name': 'Production Planning Shakti',
    'version': '17.0.0.0',
    'summary': 'To manage production planning reports.',
    'description': """To manage production planning reports.""",
    'author': ['Hardik Chauhan'],
    'category': 'sale',
    'website': 'www.teknovatesolution.com',
    'depends': ['sale', 'mrp', 'sale_management'],
    'data': [
        'views/sale_order.xml',
        'views/sale_order_line.xml',
        'views/mrp_production_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'production_planning_shakti/static/src/js/binary_field_preview.xml',
            'production_planning_shakti/static/src/js/binary_field_preview.js',
            'production_planning_shakti/static/src/js/bus_notifiction.js',
            'production_planning_shakti/sound/notify.mp3',

        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
