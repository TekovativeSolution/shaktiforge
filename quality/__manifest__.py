{
    'name': 'Quality Base Tek',
    'version': '17.0.0.0',
    'category': 'Manufacturing/Quality',
    'sequence': 50,
    'author' : "Mansi Vaghela",
    'summary': 'Basic Feature for Quality',
    'depends': ['stock'],
    'description': """
Quality Base
===============
* Define quality points that will generate quality checks on pickings,
  manufacturing orders or work orders (quality_mrp)
* Quality alerts can be created independently or related to quality checks
* Possibility to add a measure to the quality check with a min/max tolerance

""",
    'data': [
        'security/quality.xml',
        'security/ir.model.access.csv',
        'data/mail_alias_data.xml',
        'data/quality_data.xml',
        'views/quality_views.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'quality/static/src/**/*',
        ],
        # 'web.qunit_suite_tests': [
        #     'quality/static/tests/*.js',
        # ],
    }
}
