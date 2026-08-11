from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    child_mo_qty = fields.Selection([
        ('all', 'All Quantity'),
        ('required', 'Required Quantity')], string="Child MO Qty")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update({
            'child_mo_qty': params.get_param('manufacturing_recurring_tek.child_mo_qty'),
        })
        return res

    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param("manufacturing_recurring_tek.child_mo_qty",
                                                         self.child_mo_qty)
        super(ResConfigSettings, self).set_values()