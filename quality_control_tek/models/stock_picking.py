from odoo import api, fields, models, _

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        """Create stock move and move line when validate picking for fail qc."""

        res = super(StockPicking,self).button_validate()
        if self.check_ids and self.check_ids[0].point_id.picking_type_id:
            self.create_fail_qc_picking()
        return res

    def create_fail_qc_picking(self):
        """create stock move for fail qc product."""
        if self.check_ids.filtered(lambda check:check.quality_state == 'fail'):
            picking_id = self.env['stock.picking'].create({
                    'partner_id': self.partner_id.id,
                    'location_id': self.check_ids[0].point_id.picking_type_id.default_location_src_id.id,
                    'location_dest_id': self.check_ids[0].point_id.picking_type_id.default_location_dest_id.id,
                    'picking_type_id': self.check_ids[0].point_id.picking_type_id.id,
                    'state': "draft",
                    'origin': self.name,

                })
            # product_ids = self.check_ids.filtered(lambda check:check.quality_state == 'fail').mapped('product_id')
            product_list = []
            for check_id in self.check_ids.filtered(lambda check:check.quality_state == 'fail'):
                if  not check_id.product_id.id in product_list:
                    lot_name = self.check_ids.filtered(lambda check: check.quality_state == 'fail' and check_id.product_id == check.product_id).mapped('lot_name')
                    lot_ids = self.env['stock.lot'].search(
                        [('name', 'in', lot_name), ('company_id', '=', check_id.company_id.id)])
                    move_line = {
                        'product_id': check_id.product_id.id,
                        'name': check_id.product_id.name,
                        'product_uom': check_id.product_id.uom_id.id,
                        'product_uom_qty': check_id.qty_line,
                        'picking_type_id': check_id.point_id.picking_type_id.id,
                        'location_id': check_id.point_id.picking_type_id.default_location_src_id.id,
                        'location_dest_id': check_id.point_id.picking_type_id.default_location_dest_id.id,
                        'picking_id': picking_id.id,
                        'state': "draft",
                        #'lot_ids':[(6,0,lot_ids.ids)]

                    }
                    move_id = self.env['stock.move'].create(move_line)
                    for lot_id in lot_ids:
                        move_line_id = self.env['stock.move.line'].create({
                            'product_id': check_id.product_id.id,
                            'quantity': check_id.qty_line,

                            'company_id': self.company_id.id,
                            'move_id': move_id.id,
                            # 'quant_id':quant_id.id,
                            'lot_id': lot_id.id,
                            'location_id': check_id.point_id.picking_type_id.default_location_src_id.id,
                            'location_dest_id': check_id.point_id.picking_type_id.default_location_dest_id.id,
                        })
                    product_list.append(check_id.product_id.id)
            picking_id.action_confirm()
