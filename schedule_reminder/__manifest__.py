# -*- coding: utf-8 -*-

{
    'name': 'Schedule Reminder',
    'version': '17.0.0.0',
    'category': 'crm',
    'author': 'Nilesh Parmar',
    'summary': 'User can pass the date and time for schedule action and set the reminder for the activity',
    'description': "User can pass the date and time for schedule action and set the reminder for the activity",
    'website': 'http://www.teknovatesolutions.com/',
    'images': [],
    'module_type': 'official' ,
    'depends': ['mail', 'base_setup'],
    'assets': {
        'web.assets_backend': [
            'schedule_reminder/static/src/bus_notification.js',
        ],
    },
    'data': [
        'security/ir.model.access.csv',
        'data/remove_reminder_cron.xml',
        'data/schedule_activity.xml',
        'views/mail_activity_schedule.xml',
        'views/activity_reminder.xml',
        'views/mail_activity.xml',
        'views/res_config_setting.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
