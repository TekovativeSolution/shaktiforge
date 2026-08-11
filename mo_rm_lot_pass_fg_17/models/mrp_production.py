from odoo import fields, models, _, api
from odoo.exceptions import UserError
from collections import defaultdict


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def action_assign_lot_no(self):
        self.ensure_one()

        # Get all raw material move lines having lots
        raw_move_lines = self.move_raw_ids.move_line_ids.filtered(lambda l: l.lot_id)

        if not raw_move_lines:
            raise UserError(_("Please assign Lot/Serial Number to all component products first."))

        # Get unique lot names (remove duplicates)
        lot_names = sorted(set(raw_move_lines.mapped("lot_id.name")))

        # =====================================================
        # Merge Lot Validation
        # =====================================================
        if self.product_id.categ_id.is_merge_lot:
            # Allow multiple component lots
            fg_lot_name = ",".join(lot_names)
        else:
            # Allow only one component lot
            if len(lot_names) > 1:
                # "Multiple component lots are not allowed for '%s'.\n\n"
                raise UserError(_(
                    "Please use only one component and one lot.\n\n"
                    "Found Lots:\n%s"
                ) % (
                                    self.product_id.display_name,
                                    "\n".join(lot_names)
                                ))

            fg_lot_name = lot_names[0]

        # =====================================================
        # Search Finished Product Lot
        # =====================================================
        fg_lot = self.env["stock.lot"].search([
            ("name", "=", fg_lot_name),
            ("product_id", "=", self.product_id.id),
            ("company_id", "=", self.company_id.id),
        ], limit=1)

        # Create Finished Product Lot if not found
        if not fg_lot:
            fg_lot = self.env["stock.lot"].create({
                "name": fg_lot_name,
                "product_id": self.product_id.id,
                "company_id": self.company_id.id,
            })

        # Assign Finished Lot to MO
        self.lot_producing_id = fg_lot.id

        # Make sure all component move lines have their original lots
        for ml in raw_move_lines:
            if not ml.lot_id:
                raise UserError(_("Component lot is missing for product %s.") % ml.product_id.display_name)

        # Assign Finished Lot to Finished Move Lines (if already created)
        finished_moves = self.move_finished_ids.filtered(
            lambda m: m.product_id == self.product_id
        )

        for move in finished_moves:
            for ml in move.move_line_ids:
                ml.lot_id = fg_lot.id

        return True

    # def action_assign_lot_no(self):
    #     self.ensure_one()
    #     # Raw move lines having a lot
    #     raw_move_lines = self.move_raw_ids.move_line_ids.filtered(lambda l: l.lot_id)
    #
    #     if not raw_move_lines:
    #         raise UserError(_("Please reserve a raw material lot first."))
    #
    #     # First raw material lot
    #     raw_lot = raw_move_lines[0].lot_id
    #
    #     # Search FG lot
    #     fg_lot = self.env["stock.lot"].search([
    #         ("name", "=", raw_lot.name),
    #         ("product_id", "=", self.product_id.id),
    #         ("company_id", "=", self.company_id.id),
    #     ], limit=1)
    #
    #     # Create if not found
    #     if not fg_lot:
    #         fg_lot = self.env["stock.lot"].create({
    #             "name": raw_lot.name,
    #             "product_id": self.product_id.id,
    #             "company_id": self.company_id.id,
    #         })
    #
    #     # Assign finished lot
    #     self.lot_producing_id = fg_lot.id
    #
    #     # Make sure every raw move line has a lot
    #     for line in raw_move_lines:
    #         line.lot_id = raw_lot.id
    #
    #     # Update finished move
    #     finished_move = self.move_finished_ids.filtered(
    #         lambda m: m.product_id == self.product_id
    #     )
    #
    #     if finished_move:
    #         for ml in finished_move.move_line_ids:
    #             ml.lot_id = fg_lot.id
    #
    #     return True