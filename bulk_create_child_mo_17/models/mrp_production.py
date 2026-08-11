from odoo import fields, models, _, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def action_create_child_mo_multi(self):
        for mo in self:
            mo.button_create_mo()
        return True