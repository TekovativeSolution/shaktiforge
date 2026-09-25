from odoo import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # def _create_picking(self):
    #     if self.env.context.get('skip_default_picking'):
    #         return True
    #     return super()._create_picking()

    def _create_picking(self):
        for order in self.filtered(lambda po: po.state in ('purchase', 'done')):
            location_id = order.partner_id.property_stock_supplier.id

            location_dest_id = (
                order._get_destination_location()
                if hasattr(order, '_get_destination_location')
                else order.picking_type_id.default_location_dest_id.id
            )

            common_picking = False
            created_pickings = self.env['stock.picking']

            for line in order.order_line:
                if (
                        line.display_type
                        or line.product_qty <= 0
                        or line.product_id.type == 'service'
                ):
                    continue

                vals = {
                    'partner_id': order.partner_id.id,
                    'picking_type_id': order.picking_type_id.id,
                    'location_id': location_id,
                    'location_dest_id': location_dest_id,
                    'origin': order.name,
                    'company_id': order.company_id.id,
                }

                if line.product_id.categ_id.is_receipt:
                    # is_receipt = True
                    picking = self.env['stock.picking'].create(vals)
                    created_pickings |= picking
                else:
                    # is_receipt = False
                    if not common_picking:
                        common_picking = self.env['stock.picking'].create(vals)
                        created_pickings |= common_picking
                    picking = common_picking


                self.env['stock.move'].create(line._prepare_stock_moves(picking))

            #confirm + assign => Ready
            created_pickings.action_confirm()
            created_pickings.action_assign()

        return True


    # def button_confirm(self):
    #     res = super(PurchaseOrder, self.with_context(skip_default_picking=True)).button_confirm()
    #
    #     for order in self:
    #         location_id = order.partner_id.property_stock_supplier.id
    #         location_dest_id = (
    #             order._get_destination_location()
    #             if hasattr(order, '_get_destination_location')
    #             else order.picking_type_id.default_location_dest_id.id
    #         )
    #
    #         for line in order.order_line:
    #             if line.display_type or line.product_qty <= 0 or line.product_id.type == 'service':
    #                 continue
    #
    #             picking = self.env['stock.picking'].create({
    #                 'partner_id': order.partner_id.id,
    #                 'picking_type_id': order.picking_type_id.id,
    #                 'location_id': location_id,
    #                 'location_dest_id': location_dest_id,
    #                 'origin': order.name,
    #                 'purchase_id': order.id,
    #                 'company_id': order.company_id.id,
    #             })
    #
    #             self.env['stock.move'].create({
    #                 'name': line.name,
    #                 'product_id': line.product_id.id,
    #                 'product_uom_qty': line.product_qty,
    #                 'product_uom': line.product_uom.id,
    #                 'picking_id': picking.id,
    #                 'location_id': location_id,
    #                 'location_dest_id': location_dest_id,
    #                 'purchase_line_id': line.id,
    #                 'company_id': order.company_id.id,
    #             })
    #
    #             picking.action_confirm()
    #
    #     return res