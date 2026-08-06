from odoo import api, fields, models, _

class QualityPoint(models.Model):
    _inherit = "quality.point"

    quality_master_id = fields.Many2one('quality.control.master', string='Quality Master')
    picking_type_id = fields.Many2one('stock.picking.type', string='QC Fail Operation')

