from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    campaign_id = fields.Many2one('utm.campaign', string="Campaign")
    source_id = fields.Many2one('utm.source', string="Source")
    medium_id = fields.Many2one('utm.medium', string="Medium")
    # user_id = fields.Many2one('res.users', string='Salesperson')
    # team_id = fields.Many2one("crm.team", string="Sales Team")