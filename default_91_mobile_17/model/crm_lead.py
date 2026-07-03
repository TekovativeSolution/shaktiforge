from odoo import api, fields, models, _


class Lead(models.Model):
    _inherit = "crm.lead"

    @api.model
    def create(self, vals):
        res = super(Lead, self).create(vals)
        res.mobile = '+91' + '' + str(res.mobile)
        return res
