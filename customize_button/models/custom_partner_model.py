# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CustomizeButtonPartner(models.Model):
    _inherit = 'res.partner'

    def action_phone_call(self):
        for record in self:
            if record.phone and record.mobile:
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Choose Number',
                    'res_model': 'phone.call.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {'default_phone_number': record.phone or record.mobile},
                }
            elif record.phone or record.mobile:
                phone_number = (record.phone or record.mobile).replace(" ", "")
                tel_link = f"tel:{phone_number}"
                return {
                    'type': 'ir.actions.client',
                    'tag': 'call_phone',
                    'context': {'phone_number': phone_number},
                }
        return False

    # def action_send_email(self):
    #     for record in self:
    #         if record.email_from:
    #             email = record.email_from
    #             tel_link = f"mailto:{email}"
    #             return {
    #                 'type': 'ir.actions.act_url',
    #                 'url': tel_link,
    #             }
    #     return False

    def action_send_whatsapp(self):
        for record in self:
            if record.phone and record.mobile:
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Choose Number',
                    'res_model': 'phone.call.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {'default_phone_number': record.phone or record.mobile},
                }
            elif record.phone or record.mobile:
                phone_number = record.phone or record.mobile
                tel_link = f"tel:{phone_number}"
                return {
                    'type': 'ir.actions.act_url',
                    'url': tel_link,
                }
        return False


    # def action_send_whatsapp(self):
    #     for record in self:
    #         if record.mobile:
    #             mobile = record.mobile
    #             whatsapp_link = f"whatsapp://send?phone={mobile}"
    #             return {
    #                 'type': 'ir.actions.act_url',
    #                 'url': whatsapp_link,
    #             }
    #     return False

