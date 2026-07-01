from odoo import tools
from odoo import models, api, fields
import logging
_logger = logging.getLogger(__name__)

class PhoneCallWizard(models.TransientModel):
    _name = 'phone.call.wizard'
    _description = 'Phone Call Wizard'

    phone_number = fields.Char("Phone Number")
    phone_type = fields.Selection([
        ('phone', 'Phone'),
        ('mobile', 'Mobile')
    ], string="Type", required=True)

    @api.model
    def default_get(self, fields):
        res = super(PhoneCallWizard, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        if active_id:
            contact = self.env['crm.lead'].browse(active_id)
            res.update({
                'phone_number': contact.phone or contact.mobile,
                'phone_type': 'phone' if contact.phone else 'mobile',
            })
        return res

    @api.onchange('phone_type')
    def _onchange_phone_type(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            contact = self.env['crm.lead'].browse(active_id)
            if self.phone_type == 'mobile':
                self.phone_number = contact.mobile
            else:
                self.phone_number = contact.phone


    def action_call(self):
        phone_number = (self.phone_number).replace(" ", "")
        tel_link = f"tel:{phone_number}"
        return {
            'type': 'ir.actions.act_url',
            'url': tel_link,
        }