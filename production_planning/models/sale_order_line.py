from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    production_status = fields.Selection([
        ('pending', 'Pending'),
        ('planning', 'planning')
    ], string='Production Status',default='pending')
    attachment = fields.Binary(string="Attachment")

    commitment_date = fields.Datetime(
        string="Delivery Date", related='order_id.commitment_date',
        help="This is the delivery date promised to the customer. "
             "If set, the delivery order will be scheduled based on "
             "this date rather than product lead times.")

    partner_id = fields.Many2one('res.partner', related='order_id.partner_id',
        store=True, string='Customer')

    actual_qty = fields.Float(string="Actual Qnt", compute="_compute_actual_qty")
    to_order = fields.Float(string="To Order", compute="_compute_to_order")

    @api.depends('product_id')
    def _compute_actual_qty(self):
        for line in self:
            line.actual_qty = line.product_id.free_qty if line.product_id else 0.0

    @api.depends_context('product_uom_qty', 'actual_qty')
    def _compute_to_order(self):
        for rec in self:
            rec.to_order =  max(rec.product_uom_qty - rec.actual_qty, 0)

    def action_create_mo(self):
        for line in self:
            if not line.product_id:
                raise UserError(_("Please select a product."))

            # Create Manufacturing Order
            mo = self.env['mrp.production'].create({
                'origin': line.order_id.name,
                'product_id': line.product_id.id,
                'product_qty': line.to_order if line.to_order > 0 else 0.0,
                'product_uom_id': line.product_uom.id,
                'sale_order_id': line.order_id.id,
                'customer_id': line.partner_id.id,
                'attachment': line.attachment,
                'sale_description': line.name,
            })

            # Update production_status
            line.production_status = 'planning'

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'mrp.production',
                'view_mode': 'form',
                'res_id': mo.id,
            }




class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super().action_confirm()
        # Force recompute available qty at confirmation time
        for order in self:
            order.order_line._compute_actual_qty()
            order.order_line._compute_to_order()
        return res