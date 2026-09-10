from functools import reduce

from odoo import api, fields, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    heat_no = fields.Char(string="Heat No.")
    no_of_lots = fields.Integer(string="No. of Lots")
    # first_move_line_deleted = fields.Boolean(string="Is first move line deleted?")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('heat_no') and vals.get('picking_id'):
                picking = self.env['stock.picking'].browse(vals['picking_id'])
                if picking.heat_no:
                    vals['heat_no'] = picking.heat_no
        return super().create(vals_list)


    def generate_dynamic_lot(self):
        for move in self:
            material_grade = move.product_id.x_material_grade_id
            if not material_grade:
                raise UserError(
                    "Please set a Material Grade on product '%s' before generating lots."
                    % move.product_id.display_name
                )

            if move.heat_no and move.no_of_lots:
                for _dummy in range(move.no_of_lots):
                    next_number = material_grade.product_next_number
                    lot_name = "{prefix}{number}".format(
                        prefix=material_grade.product_prefix or '',
                        number=str(next_number).zfill(material_grade.product_sequence_size or 0),
                    )
                    vals = {
                        'product_id': move.product_id.id,
                        'quantity': 0,
                        'heat_no': move.heat_no,
                        'lot_name': lot_name,
                        'move_id': move.id,
                    }
                    self.env['stock.move.line'].create(vals)
                    material_grade.product_next_number = next_number + 1

                move.quantity = reduce(
                    lambda x, y: x + y, move.move_line_ids.mapped('quantity'), 0.0
                )

    # def generate_dynamic_lot(self):
    #     """Create multiple stock move lines (lots) based on Heat No. and No of Lots.
    #     Lot/Serial Number is generated from the product's Material Grade
    #     (prefix + zero-padded sequence number), and the grade's counter is
    #     incremented after every lot generated.
    #     """
    #     for move in self:
    #         material_grade = move.product_id.x_material_grade_id
    #         if not material_grade:
    #             raise UserError(
    #                 "Please set a Material Grade on product '%s' before generating lots."
    #                 % move.product_id.display_name
    #             )
    #
    #         if move.heat_no and move.no_of_lots:
    #             if not move.first_move_line_deleted and move.move_line_ids:
    #                 move.move_line_ids.unlink()
    #                 move.first_move_line_deleted = True
    #
    #             for _dummy in range(move.no_of_lots):
    #                 next_number = material_grade.product_next_number
    #                 lot_name = "{prefix}{number}".format(
    #                     prefix=material_grade.product_prefix or '',
    #                     number=str(next_number).zfill(material_grade.product_sequence_size or 0),
    #                 )
    #                 vals = {
    #                     'product_id': move.product_id.id,
    #                     'quantity': 0,
    #                     'heat_no': move.heat_no,
    #                     'lot_name': lot_name,
    #                     'move_id': move.id,
    #                 }
    #                 self.env['stock.move.line'].create(vals)
    #                 # increment the grade's counter so next lot gets the next number
    #                 material_grade.product_next_number = next_number + 1
    #
    #             move.quantity = reduce(
    #                 lambda x, y: x + y, move.move_line_ids.mapped('quantity'), 0.0
    #             )