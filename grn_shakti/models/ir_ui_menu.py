from odoo import models, api


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def _load_menus_blacklist(self):
        res = super()._load_menus_blacklist()
        if self.env.user.has_group('grn_shakti.group_qc_status_user'):
            hidden_xml_ids = [
                'stock.out_picking',
                'stock.int_picking',
                'mrp.mrp_operation_picking',
            ]
            hidden_ids = []
            for xml_id in hidden_xml_ids:
                menu = self.env.ref(xml_id, raise_if_not_found=False)
                if menu:
                    hidden_ids.append(menu.id)

            parent = self.env.ref('stock.menu_stock_transfers', raise_if_not_found=False)
            if parent:
                extra_menus = self.sudo().search([
                    ('parent_id', '=', parent.id),
                    ('name', 'in', ['Dropships', 'Batch Transfers']),
                ])
                hidden_ids += extra_menus.ids

            for menu_id in hidden_ids:
                if menu_id not in res:
                    res.append(menu_id)
        return res

# from odoo import models, api
#
# class IrUiMenu(models.Model):
#     _inherit = 'ir.ui.menu'
#
#     @api.model
#     def _load_menus_blacklist(self):
#         res = super()._load_menus_blacklist()
#         if self.env.user.has_group('grn_shakti.group_qc_status_user'):
#             hidden_xml_ids = [
#                 'stock.out_picking',          # Deliveries
#                 'stock.int_picking',          # Internal Transfers
#                 'mrp.mrp_operation_picking',  # Manufacturings
#             ]
#             for xml_id in hidden_xml_ids:
#                 menu = self.env.ref(xml_id, raise_if_not_found=False)
#                 if menu and menu.id not in res:
#                     res.append(menu.id)
#         return res