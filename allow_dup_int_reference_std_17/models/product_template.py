from odoo import models, fields, api
from odoo import _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.onchange('default_code')
    def _onchange_default_code(self):
        # Remove the check for duplicate internal reference
        if not self.default_code:
            return

        return {}


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('default_code')
    def _onchange_default_code(self):
        # Remove the check for duplicate internal reference
        if not self.default_code:
            return

        return {}
