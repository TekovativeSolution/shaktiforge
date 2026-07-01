from odoo import models, fields,api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    reminder_before = fields.Integer(string="Reminder Before",default=15)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        reminder_before = params.get_param('reminder_before')
        res.update(reminder_before=reminder_before)
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("reminder_before", self.reminder_before)
