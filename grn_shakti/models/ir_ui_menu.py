from odoo import models, api

class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def _load_menus_blacklist(self):
        res = super()._load_menus_blacklist()
        if self.env.user.has_group('grn_shakti.group_qc_status_user'):
            hidden_xml_ids = [
                'stock.out_picking',          # Deliveries
                'stock.int_picking',          # Internal Transfers
                'mrp.mrp_operation_picking',  # Manufacturings
            ]
            for xml_id in hidden_xml_ids:
                menu = self.env.ref(xml_id, raise_if_not_found=False)
                if menu and menu.id not in res:
                    res.append(menu.id)
        return res