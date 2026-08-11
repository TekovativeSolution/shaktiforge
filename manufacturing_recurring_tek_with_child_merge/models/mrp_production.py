from odoo import fields, models, _, api
from odoo.exceptions import UserError
from collections import defaultdict


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    is_child_mo = fields.Boolean(string="Is Child MO?")
    child_mo_lines = fields.One2many("child.mo.lines", "child_mo_line_id", string="Child MO Lines")
    parent_mo_lines = fields.One2many("parent.mo.lines", "parent_mo_line_id", string="Parent MO Lines")

    def create_child_mo_for_required_qty_bomwise(self):
        """Create child MOs only for components where stock is insufficient,
        with consolidated quantities.
        """
        created_mos = []

        # Get consolidated requirements for all components
        consolidated_requirements = self._get_consolidated_requirements(
            self.bom_id,
            self.product_qty
        )

        if not consolidated_requirements:
            raise UserError(
                _("No Manufacturing Orders were created. "
                  "All components have sufficient stock.")
            )

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

            # Create MO only for shortage quantity
            shortage_qty = total_required_qty - available_qty

            # Search only Draft child MO having same product & BOM
            existing_child_mo = self.env['mrp.production'].search([
                ('product_id', '=', product.id),
                ('bom_id', '=', component_bom.id),
                ('state', '=', 'draft'),
                ('is_child_mo', '=', True),
            ], limit=1)

            if existing_child_mo:

                # Increase existing Child MO quantity
                existing_child_mo.product_qty += shortage_qty

                # Create / update Child MO Lines
                self._create_or_update_child_mo_line(
                    child_mo=existing_child_mo,
                    parent_mo=self,
                    qty=shortage_qty,
                )

                # Create Parent MO Line if it does not already exist
                self._create_parent_mo_line(
                    parent_mo=self,
                    child_mo=existing_child_mo,
                )

                created_mos.append(existing_child_mo)
            else:

                mo_vals = {
                    'product_id': product.id,
                    'product_qty': shortage_qty,
                    'bom_id': component_bom.id,
                    'master_mo_id': self.id,
                    'is_child_mo': True,
                    'origin': f"{self.name} - {product.name}",
                    'picking_type_id': (
                        component_bom.picking_type_id.id
                        if component_bom.picking_type_id
                        else self.picking_type_id.id
                    ),
                }

                # Create new Child MO
                new_mo = self.env['mrp.production'].create(mo_vals)

                # Create Child MO Line
                self._create_or_update_child_mo_line(
                    child_mo=new_mo,
                    parent_mo=self,
                    qty=shortage_qty,
                )

                # Create Parent MO Line
                self._create_parent_mo_line(
                    parent_mo=self,
                    child_mo=new_mo,
                )

                created_mos.append(new_mo)

        if created_mos:
            return self._show_created_mos(created_mos)

        raise UserError(
            _("No Manufacturing Orders were created. "
              "All components have sufficient stock.")
        )

    def _create_or_update_child_mo_line(self, child_mo, parent_mo, qty):
        """Create or update Child MO Line."""

        ChildMOLines = self.env['child.mo.lines']

        line = ChildMOLines.search([
            ('child_mo_line_id', '=', child_mo.id),
            ('parent_mo_id', '=', parent_mo.id),
        ], limit=1)

        if line:
            # Existing Parent -> Child relation
            line.qty += qty
        else:
            # New Parent -> Child relation
            ChildMOLines.create({
                'child_mo_line_id': child_mo.id,
                'parent_mo_id': parent_mo.id,
                'qty': qty,
            })

    def _create_parent_mo_line(self, parent_mo, child_mo):
        """Create Parent MO Line for Parent -> Child MO relationship."""

        ParentMOLines = self.env['parent.mo.lines']

        # Check whether this Parent MO already has this Child MO
        line = ParentMOLines.search([
            ('parent_mo_line_id', '=', parent_mo.id),
            ('child_mo_id', '=', child_mo.id),
        ], limit=1)

        # Do not create duplicate Parent MO Lines
        if not line:
            ParentMOLines.create({
                'parent_mo_line_id': parent_mo.id,
                'child_mo_id': child_mo.id,
            })

    # def create_child_mo_for_required_qty_bomwise(self):
    #     """Create child MOs only for components where stock is insufficient, with consolidated quantities"""
    #     created_mos = []
    #
    #     # Get consolidated requirements for all components
    #     consolidated_requirements = self._get_consolidated_requirements(self.bom_id, self.product_qty)
    #
    #     if not consolidated_requirements:
    #         raise UserError(_("No Manufacturing Orders were created. All components have sufficient stock."))
    #
    #     # Create MOs based on consolidated requirements and stock availability
    #     for product_id, requirement_data in consolidated_requirements.items():
    #         product = self.env['product.product'].browse(product_id)
    #         total_required_qty = requirement_data['total_qty']
    #         component_bom = requirement_data['bom']
    #
    #         # Check available quantity
    #         available_qty = product.qty_available
    #
    #         # Only create MO if stock is insufficient
    #         if available_qty >= total_required_qty:
    #             continue
    #
    #         # Create MO for the shortage quantity
    #         shortage_qty = total_required_qty - available_qty
    #
    #         # Search only Draft child MO having same product & BOM
    #         existing_child_mo = self.env['mrp.production'].search([
    #             ('product_id', '=', product.id),
    #             ('bom_id', '=', component_bom.id),
    #             ('state', '=', 'draft'),
    #         ], limit=1)
    #
    #         if existing_child_mo:
    #             # Merge quantity into existing Draft MO
    #             existing_child_mo.product_qty += shortage_qty
    #             self._create_or_update_child_mo_line(existing_child_mo, self, shortage_qty)
    #
    #             # Recompute components
    #             # existing_child_mo._onchange_move_raw()
    #
    #             created_mos.append(existing_child_mo)
    #
    #         else:
    #             mo_vals = {
    #                 'product_id': product.id,
    #                 'product_qty': shortage_qty,
    #                 'bom_id': component_bom.id,
    #                 'master_mo_id': self.id,
    #                 'is_child_mo': True,
    #                 'origin': f"{self.name} - {product.name}",
    #                 'picking_type_id': component_bom.picking_type_id.id
    #                 if component_bom.picking_type_id
    #                 else self.picking_type_id.id,
    #             }
    #
    #             new_mo = self.env['mrp.production'].create(mo_vals)
    #             self._create_or_update_child_mo_line(new_mo, self, shortage_qty)
    #
    #             # Confirm only newly created MO
    #             # new_mo.action_confirm()
    #
    #             created_mos.append(new_mo)
    #
    #     if created_mos:
    #         return self._show_created_mos(created_mos)
    #     else:
    #         raise UserError(_("No Manufacturing Orders were created. All components have sufficient stock."))
    #
    # def _create_or_update_child_mo_line(self, child_mo, parent_mo, qty):
    #     ChildMOLines = self.env['child.mo.lines']
    #
    #     line = ChildMOLines.search([
    #         ('child_mo_line_id', '=', child_mo.id),
    #         ('parent_mo_id', '=', parent_mo.id),
    #     ], limit=1)
    #
    #     if line:
    #         line.qty += qty
    #     else:
    #         ChildMOLines.create({
    #             'child_mo_line_id': child_mo.id,
    #             'parent_mo_id': parent_mo.id,
    #             'qty': qty,
    #         })


class ChildMOLines(models.Model):
    _name = 'child.mo.lines'

    child_mo_line_id = fields.Many2one("mrp.production", string="Child ID")
    parent_mo_id = fields.Many2one("mrp.production", string="Parent MO")
    qty = fields.Float(string="Quantity")


class ParentMOLines(models.Model):
    _name = 'parent.mo.lines'

    parent_mo_line_id = fields.Many2one("mrp.production", string="Parent ID")
    child_mo_id = fields.Many2one("mrp.production", string="Child MO")


