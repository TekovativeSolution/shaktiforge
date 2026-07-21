from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    show_customer_info = fields.Boolean(
        string="Show Customer Name and Attachment in Manufacturing Orders",
        config_parameter='custom.mrp.show_customer_info'
    )