{
    'name': "OneSignal Notification - CRM",
    'category': 'CRM',
    'version': '17.0.0.0',
    'author': 'Piyush',
    'description': """
        OneSignal Notification.
    """,
    'summary': """OneSignal Notification""",
    'module_type': 'official' ,
    'depends': ['crm', 'odoo_one_signal_notification'],

    'website': "",
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_setting.xml',
        'views/notification_import_wizard.xml'
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: