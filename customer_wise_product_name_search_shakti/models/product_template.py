from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_customerinfo_ids = fields.One2many(
        'product.customerinfo', 'product_tmpl_id', string='Customer Price Info')



class ProductProduct(models.Model):
    _inherit = "product.product"

    product_customerinfo_ids = fields.One2many(
        'product.customerinfo', 'product_id', string='Customer Price Info')



