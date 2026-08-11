# -*- encoding: utf-8 -*-

{
    'name': 'Manufacturing Child Tek',
    'version': '1.0',
    'category': 'Manufacturing/Manufacturing',
    'sequence': 51,
    'summary': """Create recurrent MO.""",
    'depends': ['base','mrp','stock'],

    'description': """To manage mrp quality control flow.""",
    'author':'Mansi Vaghela',
    'data': [
        'security/ir.model.access.csv',

         'views/mrp_production.xml',
         'views/mrp_bom_view.xml',

        'wizard/mrp_production_wizard.xml',
        'wizard/res_config_setting.xml'

    ],
    'demo': [

    ]

}
