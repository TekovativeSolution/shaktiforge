# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
import base64

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"


    pdf_public_url = fields.Char(string="Public URL")
    def generate_public_url(self):
        """Use to generate public url for pdf."""

        if not self.pdf_public_url:
            report = self.env['ir.actions.report']._render_qweb_pdf("purchase_tek_std_17_3.custom_report_purchase_document", self.id)
            attachment_id = self.env['ir.attachment'].create({
                'name': 'Purchase',
                'type': 'binary',
                'datas': base64.b64encode(report[0]),
                'res_model': 'purchase.order',
                'res_id': self.ids[0],
                'mimetype': 'application/pdf'
            })
            attachment_id.write({
                'public': True,
            })
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            self.pdf_public_url = '%s/web/content/%d/%s' % (base_url, attachment_id.id, attachment_id.name)
            return {
                'type': 'ir.actions.act_url',
                'url': self.pdf_public_url,
                'target': 'new',
                'res_id': self.id,
            }
        else:
            return {
                'type': 'ir.actions.act_url',
                'url': self.pdf_public_url,
                'target': 'new',
                'res_id': self.id,
            }