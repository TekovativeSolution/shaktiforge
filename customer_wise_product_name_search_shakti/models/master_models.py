from odoo import api, fields, models, _


class ProductCode(models.Model):
    _name = "product.code"
    _description = 'Product Code'
    _rec_name = 'product_code'

    product_code = fields.Char('Product Code',required="1")



class ProductName(models.Model):
    _name = "product.name"
    _description = 'Product Name'
    _rec_name = 'product_name'

    product_name = fields.Char('Product Name',required="1")