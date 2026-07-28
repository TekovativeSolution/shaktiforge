from odoo import api, fields, models, _


class ProductCustomerInfo(models.Model):
    _name = "product.customerinfo"
    _inherit = ['mail.thread']
    _description = "Product Customer Info"
    _rec_name = "partner_id"
    _order = "id desc"

    # def _default_product_id(self):
    #     # product_id = self.env.get('default_product_id')
    #     # if not product_id:
    #     #     model, active_id = [self.env.context.get(k) for k in ['model', 'active_id']]
    #     #     if model == 'product.product' and active_id:
    #     #         product_id = self.env[model].browse(active_id).exists()
    #     product_id = self.env['product.product'].search([('product_tmpl_id', '=', self.product_tmpl_id.id)])
    #     return product_id

    partner_id = fields.Many2one(
        'res.partner', 'Customer',ondelete='cascade')
    product_name_id = fields.Many2one(
        'product.name', 'Customer Product Name', ondelete='cascade')
    product_code_id = fields.Many2one(
        'product.code', 'Customer Product Code', ondelete='cascade')

    description = fields.Char('Description')

    price = fields.Float(
        'Price', default=0.0, digits='Product Price')
    currency_id = fields.Many2one(
        'res.currency', 'Currency',default=lambda self: self.env.company.currency_id.id)

    product_id = fields.Many2one(
        'product.product', 'Product Variant',
        domain="[('product_tmpl_id', '=', parent.id)] if context.get('base_model_name') == 'product.template' else"
               " [('product_tmpl_id', '=', parent.product_tmpl_id)] if context.get('base_model_name') == 'product.product' else"
               " [('product_tmpl_id', '=', product_tmpl_id)] if product_tmpl_id else []",
       # default=_default_product_id,
        help="If not set, the vendor price will apply to all variants of this product.")
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product Template',
        index=True, ondelete='cascade')

    @api.model_create_multi
    def create(self, vals):
        for val_dict in vals:
            if val_dict.get('product_tmpl_id'):
                product_id = self.env['product.product'].search([('product_tmpl_id', '=', val_dict.get('product_tmpl_id'))])
                val_dict.update({'product_id':product_id.id})
        res = super(ProductCustomerInfo, self).create(vals)
        return res


