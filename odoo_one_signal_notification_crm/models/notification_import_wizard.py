from odoo import api, fields, models, _


class NotificationImportWizard(models.TransientModel):
    _name = "notification.import.wizard"
    _description = "Notification Import Wizard"

    is_import_notification_required = fields.Boolean(string="Is Import Notification Mandatory?",required="1")

    def set_import_notification(self):
            """To set default notification field."""
            self.env['ir.config_parameter'].sudo().set_param(
                "odoo_one_signal_notification_crm.is_import_notification_required",
                self.is_import_notification_required or False)

    @api.model
    def default_get(self, field_list):
        """To set default notification in field."""
        res = super(NotificationImportWizard, self).default_get(field_list)
        is_import_notification = self.env[
            "ir.config_parameter"
        ].get_param("odoo_one_signal_notification_crm.is_import_notification_required")
        res.update({
            'is_import_notification_required': is_import_notification

        })
        return res