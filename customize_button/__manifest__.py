# -*- coding: utf-8 -*-
{
    'name': "customize_button",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm', 'contacts', 'web', 'mail', 'auth_signup'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/contact_view.xml',
        'wizard/crm_wizard_view.xml',
        'wizard/crm_wizard_whatsapp_view.xml',
        'views/login_page_inherit.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # 'customize_button/static/src/js/widget_overide.js',
            'customize_button/static/src/scss/mobile_view.css',
            'views/templates.xml',
        ],

    },
}
