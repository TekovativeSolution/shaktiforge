from odoo import api, fields, models, _

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    unit_weight = fields.Float(string="Unit Weight", compute="_compute_weight", store=True, readonly=False)
    total_weight = fields.Float(string="Total Weight", compute="_compute_weight", store=True)
    box_qty = fields.Char(string="Box Qty.")

    @api.depends('product_id', 'product_uom_qty', 'product_id.product_tmpl_id.weight')
    def _compute_weight(self):
        for line in self:
            line.unit_weight = line.product_id.product_tmpl_id.weight or 0.0
            line.total_weight = line.unit_weight * line.product_uom_qty