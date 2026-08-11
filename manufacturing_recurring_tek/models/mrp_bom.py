from odoo import api, fields, models

class MrpBom(models.Model):
    _inherit = "mrp.bom"

    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type')


