# -*- encoding: utf-8 -*-

{
    'name': 'Manufacturing Child Merge Tek',
    'version': '17.0.0.1',
    'category': 'Manufacturing',
    'sequence': 51,
    'summary': """Create recurrent MO.""",
    'depends': ['manufacturing_recurring_tek', 'bulk_create_child_mo_17'],
    'description': """Same Child MO from Diffrent Parent MO Product Qty Merge.""",
    'author':'Sona Solani',
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_production.xml',
        'views/parent_mo_lines_view.xml',
        'views/child_mo_lines_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
