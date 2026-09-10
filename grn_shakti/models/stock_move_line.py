from collections import defaultdict
from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    heat_no = fields.Char(string="Heat No.")

    def _create_and_assign_production_lot(self):
        lot_vals = []
        key_to_index = {}
        key_to_mls = defaultdict(lambda: self.env['stock.move.line'])
        for ml in self:
            key = (ml.company_id.id, ml.product_id.id, ml.lot_name)
            key_to_mls[key] |= ml
            if ml.tracking != 'lot' or key not in key_to_index:
                key_to_index[key] = len(lot_vals)
                lot_vals.append(ml._prepare_new_lot_vals())

        lots = self.env['stock.lot'].create(lot_vals)
        for key, mls in key_to_mls.items():
            lot = lots[key_to_index[key]].with_prefetch(lots._ids)
            mls.write({'lot_id': lot.id})

            #### Pass the move line's own heat_no into the lot (receipt / internal only)
            if mls.heat_no and mls.picking_id.picking_type_id.code in ('incoming', 'internal'):
                mls.lot_id.heat_no = mls.heat_no