from odoo import api, fields, models, _


class ProductCategory(models.Model):
    _inherit = "product.category"

    is_merge_lot = fields.Boolean(string="Is Merge Lot Allowed?")