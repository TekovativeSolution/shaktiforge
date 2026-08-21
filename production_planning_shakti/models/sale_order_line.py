from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    production_status = fields.Selection([
        ('pending', 'Pending'),
        ('planning', 'Planning'),
        ('onhand', 'On Hand'),
    ], string='Production Status',default='pending')
    attachment = fields.Binary(string="Attachment")

    commitment_date = fields.Datetime(
        string="Delivery Date", related='order_id.commitment_date',
        help="This is the delivery date promised to the customer. "
             "If set, the delivery order will be scheduled based on "
             "this date rather than product lead times.")

    partner_id = fields.Many2one('res.partner', related='order_id.partner_id',
        store=True, string='Customer')
    # production = fields.Boolean(string="Production")

    actual_qty = fields.Float(string="Available Qnt", compute="_compute_actual_qty")

    date_order = fields.Datetime(
        related='order_id.date_order',
        string='Order Date'
    )

    to_order = fields.Float(
        string="To Order",
        compute="_compute_to_order",
        inverse="_inverse_to_order",
        store=True,
    )

    to_order_manual = fields.Boolean(
        string="Manual To Order",
        default=False,
    )

    @api.depends('product_id')
    def _compute_actual_qty(self):
        for line in self:
            line.actual_qty = line.product_id.free_qty if line.product_id else 0.0


    @api.depends('product_id')
    def _compute_actual_qty(self):
        for line in self:
            line.actual_qty = (
                line.product_id.free_qty
                if line.product_id
                else 0.0
            )

    @api.depends('product_uom_qty', 'actual_qty', 'to_order_manual')
    def _compute_to_order(self):
        for line in self:
            if not line.to_order_manual:
                line.to_order = max(
                    line.product_uom_qty - line.actual_qty,
                    0.0
                )

    def _inverse_to_order(self):
        for line in self:
            line.to_order_manual = True

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


            users =self.env['res.users'].search([])
            for user in users:
                if user.has_group('mrp.group_mrp_manager'):
                    self.env['bus.bus']._sendone(user.partner_id, 'simple_notification', {
                        'title': _("Production Reminder"),
                        'message': f"You have been new production order against {order.name} sale order." ,
                        'type': 'info',
                        'sticky': True,
                        'sound_file': '/production_planning_shakti/static/src/sound/notify.mp3',
                    })
        return res