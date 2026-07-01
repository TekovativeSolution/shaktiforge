from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class crm_lead(models.Model):
    _inherit = 'crm.lead'

    # @api.model
    # def create(self, vals):
    #     res = super(crm_lead, self).create(vals)
    #     if res and res.user_id:
    #         users = res.user_id
    #         config_id = self.env['onesignal.config'].get_config_id()
    #         if config_id:
    #             config_id.send_notification_using_firebase(users, "CRM Lead", "Hello!, New lead is created for you.",
    #                                                        res.id)
    #     return res

    def write(self, vals):
        res = super(crm_lead, self).write(vals)
        if vals.get('user_id'):
            config_id = self.env['onesignal.config'].get_config_id()
            for lead in self:
                users = lead.user_id
                if users and config_id:
                    is_import_notification = self.env['ir.config_parameter'].sudo().get_param(
                        'odoo_one_signal_notification_crm.is_import_notification_required')
                    _logger.info('================================: %s' % is_import_notification)
                    if is_import_notification:
                        msg = "Hello!, You are assigned on lead '%s'." % lead.name
                        config_id.send_notification_using_firebase(users, "CRM Lead", msg)
        return res
