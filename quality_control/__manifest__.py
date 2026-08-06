# -*- encoding: utf-8 -*-


{
    'name': 'Quality Tek',
    'version': '17.0.0.0',
    'category': 'Manufacturing/Quality',
    'sequence': 120,
    'summary': 'Control the quality of your products',
    'author' : "Mansi Vaghela",
    'website': 'https://www.teknovatesolution.com',
    'depends': ['quality'],
    'description': """
Quality Control
===============
* Define quality points that will generate quality checks on pickings,
  manufacturing orders or work orders (quality_mrp)
* Quality alerts can be created independently or related to quality checks
* Possibility to add a measure to the quality check with a min/max tolerance

""",
    'data': [
        'data/quality_control_data.xml',
        'report/worksheet_custom_reports.xml',
        'report/worksheet_custom_report_templates.xml',
        'views/quality_views.xml',
        'views/product_views.xml',
        'views/stock_move_views.xml',
        'views/stock_picking_views.xml',
        'views/stock_lot_views.xml',
        'wizard/quality_check_wizard_views.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'data/quality_control_demo.xml',
    ],
    'application': True,

    'assets': {
        'web.assets_backend': [
            'quality_control/static/src/**/*',
        ],
    }
}
