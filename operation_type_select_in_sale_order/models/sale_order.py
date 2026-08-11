from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Deliver From',
        domain="[('code', '=', 'outgoing'), ('company_id', '=', company_id), ('active', '=', True)]",
        help="Select the operation type for delivery (only active picking types)",
        tracking=True,
    )

    @api.onchange('warehouse_id')
    def _onchange_warehouse_delivery_type(self):
        """Update delivery picking type when warehouse changes"""
        if self.warehouse_id:
            if not self.delivery_picking_type_id:
                self.delivery_picking_type_id = self.warehouse_id.out_type_id
            return {
                'domain': {
                    'delivery_picking_type_id': [
                        ('code', '=', 'outgoing'),
                        ('warehouse_id', '=', self.warehouse_id.id),
                        ('company_id', '=', self.company_id.id),
                        ('active', '=', True),
                    ]
                }
            }
        else:
            self.delivery_picking_type_id = False
            return {
                'domain': {
                    'delivery_picking_type_id': [
                        ('code', '=', 'outgoing'),
                        ('company_id', '=', self.company_id.id),
                        ('active', '=', True),
                    ]
                }
            }

    @api.onchange('delivery_picking_type_id')
    def _onchange_delivery_picking_type(self):
        """Update warehouse when picking type changes"""
        if self.delivery_picking_type_id and self.delivery_picking_type_id.warehouse_id:
            if self.warehouse_id != self.delivery_picking_type_id.warehouse_id:
                self.warehouse_id = self.delivery_picking_type_id.warehouse_id

    def _prepare_picking(self):
        """Use selected delivery picking type before creation"""
        res = super()._prepare_picking()
        if self.delivery_picking_type_id:
            res['picking_type_id'] = self.delivery_picking_type_id.id
            if self.delivery_picking_type_id.default_location_src_id:
                res['location_id'] = self.delivery_picking_type_id.default_location_src_id.id
            if self.delivery_picking_type_id.default_location_dest_id:
                res['location_dest_id'] = self.delivery_picking_type_id.default_location_dest_id.id
        return res

    def action_confirm(self):
        for order in self:
            ctx = dict(self.env.context)
            if order.delivery_picking_type_id:
                ctx['force_picking_type_id'] = order.delivery_picking_type_id.id

            super(SaleOrder, order.with_context(ctx)).action_confirm()

        return True
    #     """Override to set correct operation type and locations on pickings and moves"""
    #     res = super()._action_confirm()
    #
    #     for order in self:
    #         picking_type = order.delivery_picking_type_id
    #         if not picking_type or not order.picking_ids:
    #             continue
    #
    #         src_location = picking_type.default_location_src_id
    #         dest_location = picking_type.default_location_dest_id
    #
    #         for picking in order.picking_ids:
    #             picking_vals = {}
    #
    #             # ✅ Set operation type
    #             if picking.picking_type_id != picking_type:
    #                 picking_vals['picking_type_id'] = picking_type.id
    #
    #             # ✅ Set locations from operation type
    #             if src_location:
    #                 picking_vals['location_id'] = src_location.id
    #             if dest_location:
    #                 picking_vals['location_dest_id'] = dest_location.id
    #
    #             if picking_vals:
    #                 picking.write(picking_vals)
    #
    #             # ✅ Update stock moves
    #             for move in picking.move_ids:
    #                 move_vals = {}
    #
    #                 if src_location:
    #                     move_vals['location_id'] = src_location.id
    #                 if dest_location:
    #                     move_vals['location_dest_id'] = dest_location.id
    #
    #                 if move_vals:
    #                     move.write(move_vals)
    #
    #                 # ✅ Update chained / origin moves (important for MTO / manufacturing)
    #                 if move.move_orig_ids and dest_location:
    #                     move.move_orig_ids.write({
    #                         'location_dest_id': dest_location.id
    #                     })
    #
    #         return res

    def write(self, vals):
        """Update pickings if delivery operation type changes"""
        res = super().write(vals)

        if 'delivery_picking_type_id' in vals and vals['delivery_picking_type_id']:
            picking_type = self.env['stock.picking.type'].browse(vals['delivery_picking_type_id'])

            for order in self:
                if order.picking_ids:
                    # Only update non-completed pickings
                    active_pickings = order.picking_ids.filtered(
                        lambda p: p.state not in ['done', 'cancel']
                    )

                    if active_pickings:
                        # Update locations from new picking type
                        pick_vals = {}
                        if picking_type.default_location_src_id:
                            pick_vals['location_id'] = picking_type.default_location_src_id.id
                        if picking_type.default_location_dest_id:
                            pick_vals['location_dest_id'] = picking_type.default_location_dest_id.id

                        if pick_vals:
                            active_pickings.write(pick_vals)

                            # Update moves
                            for picking in active_pickings:
                                picking.move_ids.write(pick_vals)
                                if picking.move_line_ids:
                                    picking.move_line_ids.write(pick_vals)

        return res

    @api.constrains('delivery_picking_type_id')
    def _check_delivery_picking_type(self):
        """Validate that delivery picking type is selected"""
        for order in self:
            if order.state in ['sale', 'done'] and not order.delivery_picking_type_id:
                raise ValidationError(_("Please select a delivery operation type before confirming the order."))


    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        ctx = dict(self.env.context)

        if self.delivery_picking_type_id:
            ctx['force_picking_type_id'] = self.delivery_picking_type_id.id

        return super(SaleOrder, self.with_context(ctx))._action_launch_stock_rule(
            previous_product_uom_qty
        )

class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _run_pull(self, procurements):
        ctx = self.env.context

        if ctx.get('force_picking_type_id'):
            picking_type = self.env['stock.picking.type'].browse(
                ctx['force_picking_type_id']
            )

            # ✅ procurements is a list of tuples: (procurement, rule)
            for procurement, rule in procurements:
                # 🔥 Update rule IN MEMORY (NO DB WRITE)
                rule.picking_type_id = picking_type
                rule.location_src_id = picking_type.default_location_src_id

        return super()._run_pull(procurements)

