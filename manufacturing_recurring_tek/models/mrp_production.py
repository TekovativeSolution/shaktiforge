from odoo import fields, models, _, api
from odoo.exceptions import UserError
from collections import defaultdict


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    master_mo_id = fields.Many2one("mrp.production", string="Source")
    mo_count = fields.Integer(string="Mo Count", compute="_compute_mo_count")

    def _compute_mo_count(self):
        for record in self:
            child_mo_obj = self.env['mrp.production'].search([('master_mo_id', '=', record.id)])
            record.mo_count = len(child_mo_obj.ids)

    @api.onchange('bom_id')
    def _onchange_bom_id_set_picking_type(self):
        """Set Operation Type from BoM automatically"""
        if self.bom_id and self.bom_id.picking_type_id:
            self.picking_type_id = self.bom_id.picking_type_id.id

    def action_view_child_mo(self):
        child_mo_obj = self.env['mrp.production'].search([('master_mo_id', '=', self.id)])
        return {
            'name': 'Child Manufacturing Orders',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': 'mrp.production',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', child_mo_obj.ids)],
            'target': 'current',
        }

    def button_create_mo(self):
        """Create Manufacturing Orders BOM-wise based on configuration"""
        if not self.bom_id:
            raise UserError(_("Please select a Bill of Materials before creating child orders."))

        child_mo_qty = self.env['ir.config_parameter'].sudo().get_param('manufacturing_recurring_tek.child_mo_qty')

        if child_mo_qty == 'required':
            return self.create_child_mo_for_required_qty_bomwise()
        elif child_mo_qty == 'all':
            return self.create_child_mo_for_all_qty_bomwise()
        else:
            # Default behavior - create for all components that have BOMs
            return self.create_child_mo_for_all_qty_bomwise()

    def create_child_mo_for_all_qty_bomwise(self):
        """Create child MOs for all components that have BOMs, with consolidated quantities"""
        created_mos = []

        # Get consolidated requirements for all components
        consolidated_requirements = self._get_consolidated_requirements(self.bom_id, self.product_qty)

        if not consolidated_requirements:
            raise UserError(_("No Manufacturing Orders were created. Check if components have valid BOMs."))

        # Create MOs based on consolidated requirements
        for product_id, requirement_data in consolidated_requirements.items():
            product = self.env['product.product'].browse(product_id)
            total_qty = requirement_data['total_qty']
            component_bom = requirement_data['bom']

            mo_vals = {
                'product_id': product.id,
                'product_qty': total_qty,
                'bom_id': component_bom.id,
                'master_mo_id': self.id,
                # 'origin': f"{self.name} - {product.name} (Total: {total_qty})",
                'origin': f"{self.name} - {product.name}",
                'picking_type_id': component_bom.picking_type_id.id if component_bom.picking_type_id else self.picking_type_id.id,
            }

            new_mo = self.env['mrp.production'].create(mo_vals)
            created_mos.append(new_mo)

        if created_mos:
            return self._show_created_mos(created_mos)
        else:
            raise UserError(_("No Manufacturing Orders were created. Check if components have valid BOMs."))

    def create_child_mo_for_required_qty_bomwise(self):
        """Create child MOs only for components where stock is insufficient, with consolidated quantities"""
        created_mos = []

        # Get consolidated requirements for all components
        consolidated_requirements = self._get_consolidated_requirements(self.bom_id, self.product_qty)

        if not consolidated_requirements:
            raise UserError(_("No Manufacturing Orders were created. All components have sufficient stock."))

        # Create MOs based on consolidated requirements and stock availability
        for product_id, requirement_data in consolidated_requirements.items():
            product = self.env['product.product'].browse(product_id)
            total_required_qty = requirement_data['total_qty']
            component_bom = requirement_data['bom']

            # Check available quantity
            available_qty = product.qty_available

            # Only create MO if stock is insufficient
            if available_qty >= total_required_qty:
                continue

            # Create MO for the shortage quantity
            shortage_qty = total_required_qty - available_qty

            mo_vals = {
                'product_id': product.id,
                'product_qty': shortage_qty,
                'bom_id': component_bom.id,
                'master_mo_id': self.id,
                'origin': f"{self.name} - {product.name}",
                # 'origin': f"{self.name} - {product.name} (Shortage: {shortage_qty})",
                'picking_type_id': component_bom.picking_type_id.id if component_bom.picking_type_id else self.picking_type_id.id,
            }

            new_mo = self.env['mrp.production'].create(mo_vals)
            # Optionally confirm the MO immediately
            new_mo.action_confirm()
            created_mos.append(new_mo)

        if created_mos:
            return self._show_created_mos(created_mos)
        else:
            raise UserError(_("No Manufacturing Orders were created. All components have sufficient stock."))

    def _get_consolidated_requirements(self, bom, quantity_needed, consolidated_dict=None, processed_boms=None):
        """
        Get consolidated requirements for all components across the entire BOM hierarchy
        Returns a dictionary with product_id as key and total required quantity as value
        """
        if consolidated_dict is None:
            consolidated_dict = {}

        if processed_boms is None:
            processed_boms = set()

        # Avoid infinite recursion for circular BOMs
        if bom.id in processed_boms:
            return consolidated_dict

        processed_boms.add(bom.id)

        for bom_line in bom.bom_line_ids:
            product = bom_line.product_id

            # Calculate required quantity based on BOM line quantity
            required_qty = (bom_line.product_qty * quantity_needed) / bom.product_qty

            # Check if this product has a BOM
            component_bom = self.env['mrp.bom'].search([
                ('product_id', '=', product.id),
                ('type', '=', 'normal')
            ], limit=1)

            if not component_bom:
                # Try with product template
                component_bom = self.env['mrp.bom'].search([
                    ('product_tmpl_id', '=', product.product_tmpl_id.id),
                    ('type', '=', 'normal')
                ], limit=1)

            if component_bom:
                # Add to consolidated requirements
                if product.id in consolidated_dict:
                    consolidated_dict[product.id]['total_qty'] += required_qty
                    consolidated_dict[product.id]['occurrences'] += 1
                else:
                    consolidated_dict[product.id] = {
                        'total_qty': required_qty,
                        'bom': component_bom,
                        'occurrences': 1,
                        'sources': []
                    }

                # Track where this component is used
                consolidated_dict[product.id]['sources'].append({
                    'parent_bom': bom.display_name,
                    'qty': required_qty
                })

                # Recursively process this BOM's components
                self._get_consolidated_requirements(
                    component_bom,
                    required_qty,
                    consolidated_dict,
                    processed_boms.copy()  # Use copy to avoid affecting other branches
                )

        return consolidated_dict

    def _show_created_mos(self, created_mos):
        """Show the created Manufacturing Orders in a tree view"""
        mo_ids = [mo.id for mo in created_mos]

        return {
            'name': _('Created Manufacturing Orders'),
            'view_mode': 'tree,form',
            'res_model': 'mrp.production',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', mo_ids)],
            'target': 'current',
            'context': {
                'default_master_mo_id': self.id,
            }
        }

    def get_bom_hierarchy_with_consolidated_requirements(self):
        """
        Helper method to visualize BOM hierarchy with consolidated requirements
        Useful for debugging and understanding component usage
        """
        if not self.bom_id:
            return {}

        # Get consolidated requirements
        consolidated_requirements = self._get_consolidated_requirements(self.bom_id, self.product_qty)

        def build_hierarchy(bom, level=0, processed_boms=None):
            if processed_boms is None:
                processed_boms = set()

            if bom.id in processed_boms:
                return {
                    'bom': f"{bom.display_name} (CIRCULAR REFERENCE)",
                    'product': bom.product_id.name if bom.product_id else bom.product_tmpl_id.name,
                    'level': level,
                    'components': []
                }

            processed_boms.add(bom.id)

            hierarchy = {
                'bom': bom.display_name,
                'product': bom.product_id.name if bom.product_id else bom.product_tmpl_id.name,
                'level': level,
                'components': []
            }

            for line in bom.bom_line_ids:
                component_info = {
                    'product': line.product_id.name,
                    'qty': line.product_qty,
                    'level': level + 1,
                    'has_bom': False
                }

                # Add consolidated requirement info if available
                if line.product_id.id in consolidated_requirements:
                    req_data = consolidated_requirements[line.product_id.id]
                    component_info.update({
                        'has_bom': True,
                        'total_consolidated_qty': req_data['total_qty'],
                        'used_in_places': req_data['occurrences'],
                        'usage_details': req_data['sources']
                    })

                    component_bom = req_data['bom']
                    component_info['sub_components'] = build_hierarchy(
                        component_bom, level + 1, processed_boms.copy()
                    )

                hierarchy['components'].append(component_info)

            return hierarchy

        return {
            'hierarchy': build_hierarchy(self.bom_id),
            'consolidated_requirements': consolidated_requirements
        }

    def get_consolidated_requirements_report(self):
        """Generate a user-friendly report of consolidated requirements"""
        if not self.bom_id:
            return "No BOM selected"

        consolidated_requirements = self._get_consolidated_requirements(self.bom_id, self.product_qty)

        if not consolidated_requirements:
            return "No components with BOMs found"

        report_lines = ["CONSOLIDATED MANUFACTURING REQUIREMENTS REPORT"]
        report_lines.append("=" * 50)
        report_lines.append(f"Master Product: {self.product_id.name}")
        report_lines.append(f"Quantity to Produce: {self.product_qty}")
        report_lines.append("")

        for product_id, req_data in consolidated_requirements.items():
            product = self.env['product.product'].browse(product_id)
            report_lines.append(f"Component: {product.name}")
            report_lines.append(f"  Total Required: {req_data['total_qty']}")
            report_lines.append(f"  Used in {req_data['occurrences']} place(s)")
            report_lines.append(f"  Available Stock: {product.qty_available}")

            shortage = req_data['total_qty'] - product.qty_available
            if shortage > 0:
                report_lines.append(f"  SHORTAGE: {shortage}")
            else:
                report_lines.append(f"  Surplus: {abs(shortage)}")

            report_lines.append("  Usage Details:")
            for source in req_data['sources']:
                report_lines.append(f"    - From {source['parent_bom']}: {source['qty']}")
            report_lines.append("")

        return "\n".join(report_lines)


# from odoo import fields, models, _, api
# from odoo.exceptions import UserError
#
#
# class MrpProduction(models.Model):
#     _inherit = 'mrp.production'
#
#     master_mo_id = fields.Many2one("mrp.production", string="Source")
#     mo_count = fields.Integer(string="Mo Count", compute="_compute_mo_count")
#
#     def _compute_mo_count(self):
#         for record in self:
#             child_mo_obj = self.env['mrp.production'].search([('master_mo_id', '=', record.id)])
#             record.mo_count = len(child_mo_obj.ids)
#
#     @api.onchange('bom_id')
#     def _onchange_bom_id_set_picking_type(self):
#         """Set Operation Type from BoM automatically"""
#         if self.bom_id and self.bom_id.picking_type_id:
#             self.picking_type_id = self.bom_id.picking_type_id.id
#
#     def action_view_child_mo(self):
#         child_mo_obj = self.env['mrp.production'].search([('master_mo_id', '=', self.id)])
#         return {
#             'name': 'Child Manufacturing Orders',
#             'view_mode': 'tree,form',
#             'view_id': False,
#             'res_model': 'mrp.production',
#             'type': 'ir.actions.act_window',
#             'domain': [('id', 'in', child_mo_obj.ids)],
#             'target': 'current',
#         }
#
#     def button_create_mo(self):
#         """Create Manufacturing Orders BOM-wise based on configuration"""
#         if not self.bom_id:
#             raise UserError(_("Please select a Bill of Materials before creating child orders."))
#
#         child_mo_qty = self.env['ir.config_parameter'].sudo().get_param('manufacturing_recurring_tek.child_mo_qty')
#
#         if child_mo_qty == 'required':
#             return self.create_child_mo_for_required_qty_bomwise()
#         elif child_mo_qty == 'all':
#             return self.create_child_mo_for_all_qty_bomwise()
#         else:
#             # Default behavior - create for all components that have BOMs
#             return self.create_child_mo_for_all_qty_bomwise()
#
#     def create_child_mo_for_all_qty_bomwise(self):
#         """Create child MOs for all components that have BOMs, organized by BOM"""
#         created_mos = []
#         processed_products = set()
#
#         # Get all BOM lines from the current production order's BOM
#         if not self.bom_id or not self.bom_id.bom_line_ids:
#             raise UserError(_("No BOM lines found for the selected BOM."))
#
#         # Process each level of the BOM hierarchy
#         self._create_mos_recursive(self.bom_id, self.product_qty, processed_products, created_mos)
#
#         if created_mos:
#             # Show created MOs
#             return self._show_created_mos(created_mos)
#         else:
#             raise UserError(_("No Manufacturing Orders were created. Check if components have valid BOMs."))
#
#     def create_child_mo_for_required_qty_bomwise(self):
#         """Create child MOs only for components where stock is insufficient"""
#         created_mos = []
#         processed_products = set()
#
#         if not self.bom_id or not self.bom_id.bom_line_ids:
#             raise UserError(_("No BOM lines found for the selected BOM."))
#
#         # Process each level considering stock availability
#         self._create_mos_recursive_required(self.bom_id, self.product_qty, processed_products, created_mos)
#
#         if created_mos:
#             return self._show_created_mos(created_mos)
#         else:
#             raise UserError(_("No Manufacturing Orders were created. All components have sufficient stock."))
#
#     def _create_mos_recursive(self, bom, quantity_needed, processed_products, created_mos):
#         """Recursively create MOs for all components that have BOMs"""
#
#         for bom_line in bom.bom_line_ids:
#             product = bom_line.product_id
#
#             # Skip if already processed
#             if product.id in processed_products:
#                 continue
#
#             # Calculate required quantity based on BOM line quantity
#             required_qty = (bom_line.product_qty * quantity_needed) / bom.product_qty
#
#             # Check if this product has a BOM
#             component_bom = self.env['mrp.bom'].search([
#                 ('product_id', '=', product.id),
#                 ('type', '=', 'normal')
#             ], limit=1)
#
#             if not component_bom:
#                 # Try with product template
#                 component_bom = self.env['mrp.bom'].search([
#                     ('product_tmpl_id', '=', product.product_tmpl_id.id),
#                     ('type', '=', 'normal')
#                 ], limit=1)
#
#             if component_bom:
#                 # Create MO for this component
#                 mo_vals = {
#                     'product_id': product.id,
#                     'product_qty': required_qty,
#                     'bom_id': component_bom.id,
#                     'master_mo_id': self.id,
#                     'origin': f"{self.name} - {product.name}",
#                     'picking_type_id': component_bom.picking_type_id.id if component_bom.picking_type_id else self.picking_type_id.id,
#                 }
#
#                 new_mo = self.env['mrp.production'].create(mo_vals)
#                 created_mos.append(new_mo)
#                 processed_products.add(product.id)
#
#                 # Recursively process this BOM's components
#                 self._create_mos_recursive(component_bom, required_qty, processed_products, created_mos)
#
#     def _create_mos_recursive_required(self, bom, quantity_needed, processed_products, created_mos):
#         """Recursively create MOs only for components with insufficient stock"""
#
#         for bom_line in bom.bom_line_ids:
#             product = bom_line.product_id
#
#             # Skip if already processed
#             if product.id in processed_products:
#                 continue
#
#             # Calculate required quantity based on BOM line quantity
#             required_qty = (bom_line.product_qty * quantity_needed) / bom.product_qty
#
#             # Check available quantity
#             available_qty = product.qty_available
#
#             # Only create MO if stock is insufficient
#             if available_qty >= required_qty:
#                 continue
#
#             # Check if this product has a BOM
#             component_bom = self.env['mrp.bom'].search([
#                 ('product_id', '=', product.id),
#                 ('type', '=', 'normal')
#             ], limit=1)
#
#             if not component_bom:
#                 # Try with product template
#                 component_bom = self.env['mrp.bom'].search([
#                     ('product_tmpl_id', '=', product.product_tmpl_id.id),
#                     ('type', '=', 'normal')
#                 ], limit=1)
#
#             if component_bom:
#                 # Create MO for the shortage quantity
#                 shortage_qty = required_qty - available_qty
#
#                 mo_vals = {
#                     'product_id': product.id,
#                     'product_qty': shortage_qty,
#                     'bom_id': component_bom.id,
#                     'master_mo_id': self.id,
#                     'origin': f"{self.name} - {product.name} (Shortage: {shortage_qty})",
#                     'picking_type_id': component_bom.picking_type_id.id if component_bom.picking_type_id else self.picking_type_id.id,
#                 }
#
#                 new_mo = self.env['mrp.production'].create(mo_vals)
#                 # Optionally confirm the MO immediately
#                 new_mo.action_confirm()
#                 created_mos.append(new_mo)
#                 processed_products.add(product.id)
#
#                 # Recursively process this BOM's components
#                 self._create_mos_recursive_required(component_bom, shortage_qty, processed_products, created_mos)
#
#     def _show_created_mos(self, created_mos):
#         """Show the created Manufacturing Orders in a tree view"""
#         mo_ids = [mo.id for mo in created_mos]
#
#         return {
#             'name': _('Created Manufacturing Orders'),
#             'view_mode': 'tree,form',
#             'res_model': 'mrp.production',
#             'type': 'ir.actions.act_window',
#             'domain': [('id', 'in', mo_ids)],
#             'target': 'current',
#             'context': {
#                 'default_master_mo_id': self.id,
#             }
#         }
#
#     def get_bom_hierarchy(self):
#         """Helper method to visualize BOM hierarchy - useful for debugging"""
#         if not self.bom_id:
#             return {}
#
#         def build_hierarchy(bom, level=0):
#             hierarchy = {
#                 'bom': bom.display_name,
#                 'product': bom.product_id.name if bom.product_id else bom.product_tmpl_id.name,
#                 'level': level,
#                 'components': []
#             }
#
#             for line in bom.bom_line_ids:
#                 component_bom = self.env['mrp.bom'].search([
#                     ('product_id', '=', line.product_id.id),
#                     ('type', '=', 'normal')
#                 ], limit=1)
#
#                 if component_bom:
#                     hierarchy['components'].append(build_hierarchy(component_bom, level + 1))
#                 else:
#                     hierarchy['components'].append({
#                         'product': line.product_id.name,
#                         'qty': line.product_qty,
#                         'level': level + 1,
#                         'has_bom': False
#                     })
#
#             return hierarchy
#
#         return build_hierarchy(self.bom_id)

# from odoo import fields, models, _, api
#
#
# class MrpProduction(models.Model):
#     _inherit = 'mrp.production'
#
#     master_mo_id = fields.Many2one("mrp.production", string="Source",)
#     mo_count = fields.Integer(string="Mo Count",compute="_compute_mo_count")
#
#     def _compute_mo_count(self):
#         child_mo_obj = self.env['mrp.production'].search([('master_mo_id', '=', self.id)])
#         self.mo_count = len(child_mo_obj.ids)
#
#     @api.onchange('bom_id')
#     def _onchange_bom_id_set_picking_type(self):
#         """Set Operation Type from BoM automatically"""
#         if self.bom_id and self.bom_id.picking_type_id:
#             self.picking_type_id = self.bom_id.picking_type_id.id
#
#     # def button_create_mo(self):
#     #         """:fun: Open mo wizard."""
#     #
#     #         view = self.env.ref('manufacturing_recurring_tek.mrp_production_wizard_form_view')
#     #         context = dict(self.env.context) or {}
#     #         mrp_id = self.env['mrp.production.wizard'].create({
#     #             'mrp_id': self.id,
#     #
#     #
#     #         })
#     #         production_lines = self.create_recurrent_mo(mrp_id)
#     #         context.update({'default_mrp_id': self.id,
#     #                          'default_production_line': mrp_id.production_line.ids,
#     #                         #'default_customer_id': self.partner_id.id
#     #                         })
#     #         return {
#     #             'name': _('Create Order'),
#     #             'type': 'ir.actions.act_window',
#     #             'view_type': 'form',
#     #             'view_mode': 'form',
#     #             'res_model': 'mrp.production.wizard',
#     #             'views': [(view.id, 'form')],
#     #             'view_id': view.id,
#     #             'target': 'new',
#     #             'context': context,
#     #         }
#
#     # def create_recurrent_mo(self,mrp_id):
#     #     """To create recurrent mo."""
#     #     vals = []
#     #     for move_id in self.move_raw_ids:
#     #
#     #         bom_id = self.env['mrp.bom'].search([('product_tmpl_id', '=', move_id.product_id.product_tmpl_id.id)])
#     #         if bom_id:
#     #             product_id = self.env['product.product'].search([('product_tmpl_id','=',bom_id.product_tmpl_id.id)])
#     #             quant_id = self.env['stock.quant'].search([('product_id','=',product_id.id),('location_id','=',move_id.location_id.id)])
#     #             if quant_id and quant_id.inventory_quantity_auto_apply < move_id.product_uom_qty:
#     #                 vals += [(0, 0, {'production_wizard_id':mrp_id.id,
#     #                             'product_id': product_id.id,
#     #                              'uom_id': product_id.uom_id.id,
#     #                              'available_qty':quant_id.inventory_quantity_auto_apply,
#     #                             #  'location_id':move_id.location_id.id,
#     #                              'need_qty':abs( move_id.product_uom_qty - quant_id.inventory_quantity_auto_apply),}),
#     #                      ]
#     #             if not quant_id:
#     #                 vals += [(0, 0, {'production_wizard_id': mrp_id.id,
#     #                                  'product_id': product_id.id,
#     #                                  'uom_id': product_id.uom_id.id,
#     #                                  'available_qty': 0,
#     #                                  #'location_id': move_id.location_id.id,
#     #                                  'need_qty': abs(
#     #                                      move_id.product_uom_qty), }),
#     #                          ]
#     #
#     #
#     #     production_line = mrp_id.write({'production_line':vals})
#     #     return production_line
#     #
#
#     def action_view_child_mo(self):
#         child_mo_obj = self.env['mrp.production'].search([('master_mo_id', '=', self.id)])
#         return {
#             'name': 'MRP Production',
#             'view_type': self.env.ref('mrp.mrp_production_tree_view').id,
#             'view_mode': 'tree,form',
#             'view_id': False,
#             'res_model': 'mrp.production',
#             'type': 'ir.actions.act_window',
#             'domain': [('id', 'in', child_mo_obj.ids)],
#             'target': 'current',
#         }
#
#
#     def button_create_mo(self):
#         """To create recurrent mo."""
#
#         child_mo_qty = self.env['ir.config_parameter'].sudo().get_param('manufacturing_recurring_tek.child_mo_qty')
#         if child_mo_qty == 'required':
#             self.create_child_mo_for_required_qty()
#         if child_mo_qty == 'all':
#             self.create_child_mo_for_all_qty()
#
#     def create_child_mo_for_all_qty(self):
#         new_mo_id = []
#         moves_to_recalculate = self.move_raw_ids
#         current_moves = self.move_raw_ids
#
#         while current_moves:
#             bom_ids = self.env['mrp.bom'].search([('product_tmpl_id', 'in', current_moves.mapped('product_tmpl_id').ids),('type','=','normal')])
#             if bom_ids:
#                 for bom_id in bom_ids:
#                     move_id = self.move_raw_ids.filtered(
#                         lambda move: move.product_id.product_tmpl_id == bom_id.product_tmpl_id)
#                     if move_id:
#                         vals = {
#                             'product_id': bom_id.product_tmpl_id.product_variant_id.id,
#                             'product_qty': move_id.product_uom_qty,
#                             'master_mo_id': self.id,
#                         }
#                         mo_id = self.env['mrp.production'].create(vals)
#                         new_mo_id.append(mo_id.id)
#                     else:
#                         mo_id = self.env['mrp.production'].search([('id','in',new_mo_id)])
#                         move_id = mo_id.move_raw_ids.filtered(
#                             lambda move: move.product_id.product_tmpl_id == bom_id.product_tmpl_id)
#                         vals = {
#
#                             'product_id': bom_id.product_tmpl_id.product_variant_id.id,
#                             'product_qty': move_id.product_uom_qty ,
#                             'master_mo_id': self.id,
#
#                         }
#                         mo_id = self.env['mrp.production'].create(vals)
#                         new_mo_id.append(mo_id.id)
#
#                     current_moves |= mo_id.move_raw_ids
#                 current_moves -= moves_to_recalculate
#                 moves_to_recalculate |= current_moves
#
#             else:
#                 current_moves -= moves_to_recalculate
#
#     def create_child_mo_for_required_qty(self):
#         new_mo_id = []
#         moves_to_recalculate = self.move_raw_ids
#         current_moves = self.move_raw_ids
#
#         while current_moves:
#             bom_ids = self.env['mrp.bom'].search(
#                 [('product_tmpl_id', 'in', current_moves.mapped('product_tmpl_id').ids),('type','=','normal')])
#             if bom_ids:
#                 for bom_id in bom_ids:
#                     move_id = self.move_raw_ids.filtered(
#                         lambda move: move.product_id.product_tmpl_id == bom_id.product_tmpl_id)
#                     if move_id:
#                         if move_id.product_uom_qty > move_id.quantity:
#                             vals = {
#                                 'product_id': bom_id.product_tmpl_id.product_variant_id.id,
#                                 'product_qty': move_id.product_uom_qty - move_id.quantity,
#                                 'master_mo_id': self.id,
#                             }
#                             mo_id = self.env['mrp.production'].create(vals)
#                             mo_id.action_confirm()
#                             new_mo_id.append(mo_id.id)
#                     else:
#                         mo_id = self.env['mrp.production'].search([('id', 'in', new_mo_id)])
#                         move_id = mo_id.move_raw_ids.filtered(
#                             lambda move: move.product_id.product_tmpl_id == bom_id.product_tmpl_id)
#                         if move_id.product_uom_qty > move_id.quantity:
#                             vals = {
#
#                                 'product_id': bom_id.product_tmpl_id.product_variant_id.id,
#                                 'product_qty': move_id.product_uom_qty - move_id.quantity,
#                                 'master_mo_id': self.id,
#
#                             }
#                             mo_id = self.env['mrp.production'].create(vals)
#                             mo_id.action_confirm()
#                             new_mo_id.append(mo_id.id)
#
#                         current_moves |= mo_id.move_raw_ids
#                 current_moves -= moves_to_recalculate
#                 moves_to_recalculate |= current_moves
#
#             else:
#                 current_moves -= moves_to_recalculate
#
#
#
