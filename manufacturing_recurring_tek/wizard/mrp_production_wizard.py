from odoo import fields, models, _, api

class MrpProductionWizard(models.Model):
    _name = 'mrp.production.wizard'
    _description = "MRP Production Wizard"

    mrp_id = fields.Many2one('mrp.production',string="MRP Production")
    production_line = fields.One2many(
        'mrp.production.line.wizard',
        'production_wizard_id',
        string="Order Lines",
        copy=True)


    def create_mo(self):
        """Create mo from create order wizard"""

        for line in self.production_line:
            vals = {

            'product_id': line.product_id.id,
            'product_qty': line.need_qty,
            'origin': self.mrp_id.name
            }
            mo_id = self.env['mrp.production'].create(vals)



class MrpProductionLineWizard(models.Model):
    _name = 'mrp.production.line.wizard'
    _description = "MRP Production Line Wizard"

    production_wizard_id = fields.Many2one('mrp.production.wizard',string="Production Wizard")
    product_id = fields.Many2one('product.product', string="Product")
    uom_id = fields.Many2one('uom.uom', string="UOM")
    available_qty = fields.Float(string="Available Qty")
    need_qty = fields.Float(string="Need Qty")
