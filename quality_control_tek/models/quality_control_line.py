from odoo import api, fields, models, _

class QualityControlLine(models.Model):
    _name = "quality.control.line"
    _description = "Quality Control Line"

    def _get_default_test_type_id(self):
        domain = self._get_type_default_domain()
        return self.env['quality.point.test_type'].search(domain, limit=1).id

    def _get_type_default_domain(self):
        return []

    name = fields.Char(
        'Title', copy=False,
        required=True)
    test_type_id = fields.Many2one('quality.point.test_type', 'Test Type',
                                   help="Defines the type of the quality control point.",
                                   default=_get_default_test_type_id)
    test_type = fields.Char(related='test_type_id.technical_name', readonly=True)
    norm = fields.Float('Norm', digits='Quality Tests')  # TDE RENAME ?
    tolerance_min = fields.Float('Min Tolerance', digits='Quality Tests')
    tolerance_max = fields.Float('Max Tolerance', digits='Quality Tests')
    norm_unit = fields.Char('Norm Unit', default=lambda self: 'mm')
    note = fields.Html('Note')
    instruction  = fields.Html('Instruction')
    failure_message = fields.Html('Failure Message')
    quality_control_id = fields.Many2one('quality.control.master', 'Quality Control')