from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleSequence(models.Model):
    _name = "sale.sequence"
    _description = "Student tag"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name")
    sequence_name = fields.Char(string="Sequence")
    operation_type = fields.Many2one('stock.picking.type', string="Operation Type")

    @api.model
    def create(self, vals):
        print("\nCreating Sale Sequence")
        sequence = self.env['ir.sequence'].create({
            'code': 'sale.order',
            'name': f'{vals["sequence_name"]}',
            'prefix': f'{vals["sequence_name"]}',
            'padding': 5,
        })
        print("\nSale Sequence:", sequence)

        return super().create(vals)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_sequence = fields.Many2one("sale.sequence", string="Sequence")

    @api.model
    def create(self, vals):
        sequence_id = vals.get('sale_sequence')

        if not sequence_id:
            raise UserError("Please select a Sale Sequence.")

        # Get prefix record
        sale_sequence = self.env['sale.sequence'].browse(sequence_id)

        print(sale_sequence.sequence_name)

        # Find related ir.sequence
        ir_sequence = self.env['ir.sequence'].search([
            ('name', '=', f'{sale_sequence.sequence_name}')
        ], limit=1)

        if not ir_sequence:
            raise UserError("Sequence not found for selected prefix.")

        # Ensure prefix matche
        vals['name'] = ir_sequence.next_by_id()

        # Create record with updated name
        return super().create(vals)

    @api.onchange("sale_sequence")
    def _onchange_sale_sequence_operation_type(self):
        for order in self:
            if order.sale_sequence and order.sale_sequence.operation_type:
                operation_type = order.sale_sequence.operation_type
                order.delivery_picking_type_id = operation_type
            else:
                order.delivery_picking_type_id = False
