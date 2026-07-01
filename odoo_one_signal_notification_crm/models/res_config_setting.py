from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_import_notification_required = fields.Boolean(string="Is Import Notification Mandatory?")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            is_import_notification_required=(params.get_param('odoo_one_signal_notification_crm.is_import_notification_required', default=False)) or False,
        )
        return res

    def set_values(self):
        self.ensure_one()
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("odoo_one_signal_notification_crm.is_import_notification_required",
                                                         self.is_import_notification_required or False)