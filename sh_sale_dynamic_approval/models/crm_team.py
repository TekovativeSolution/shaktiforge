from odoo import fields, models


class CRMTeam(models.Model):
    _inherit = 'crm.team'

    sale_approval_config_id = fields.Many2one('sh.sale.approval.config',string="Sale Approval Configuration")