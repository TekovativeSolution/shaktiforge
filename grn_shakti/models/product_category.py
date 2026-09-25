from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    is_receipt = fields.Boolean(
        string="Is Receipt",
        default=False
    )