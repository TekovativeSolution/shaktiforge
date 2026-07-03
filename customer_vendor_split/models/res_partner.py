from odoo import fields, models, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_customer_invoice = fields.Boolean(string="Is Customer?")
    is_vendor_bills = fields.Boolean(string="Is Vendor?")
