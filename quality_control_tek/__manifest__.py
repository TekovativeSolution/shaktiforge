# -*- coding: utf-8 -*-
{
    'name' : 'Quality Control Tek',
    'version' : '1.1',
    'summary': 'To manage quality control operations.',
    'description': 'To manage quality control operations.',
    'author' : "Mansi Vaghela",
    'category': 'Manufacturing/Quality',
    'website': 'https://www.teknovatesolution.com',
    'depends' : ['quality_control'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/quality_control_master.xml',
        'views/quality_control_line.xml',
        'views/quality_point.xml',
        'views/quality_check_wizard.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
