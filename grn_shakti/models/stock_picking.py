from odoo import api, fields, models
from odoo.osv import expression


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    mill_tc_no = fields.Char(string="Mill TC No.")
    heat_no = fields.Char(string="Heat No.")
    mill_ts_wt = fields.Char(string="Mill TC (Wt.)")
    no_of_recieved = fields.Integer(string="No of Recieved (Bags/Billets/RCS)")
    lab_chemical_testing_tc_no = fields.Char(string="Lab Chemical Test TC No.")
    qc_status = fields.Selection([("qc_pending","QC pending"),("transfer_to_qc","Transfer to QC"),("qc_done","QC done")],default="qc_pending",string="QC Status")

    qc_status_locked = fields.Boolean(string="QC Status Locked", copy=False, default=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('qc_status') == 'transfer_to_qc':
                vals['qc_status_locked'] = True
        return super().create(vals_list)

    reciept_of_material_verified_by = fields.Many2one('res.users',string="Reciept of Material Verified By.")
    grn_verified_and_approved_by = fields.Many2one('res.users', string="GRN Verified and Approved By.")

    # def _search(self, domain, *args, **kwargs):
    #     if self.env.user.has_group('grn_shakti.group_qc_status_user'):
    #         domain = domain + [
    #             ('picking_type_id.code', '=', 'incoming'),
    #             ('qc_status', '=', 'transfer_to_qc'),
    #         ]
    #     return super()._search(domain, *args, **kwargs)

    def write(self, vals):
        res = super().write(vals)
        if 'heat_no' in vals:
            for picking in self:
                picking.move_ids.write({'heat_no': picking.heat_no})
        if vals.get('qc_status') == 'transfer_to_qc':
            for picking in self:
                if not picking.qc_status_locked:
                    picking.qc_status_locked = True
        return res

    def _search(self, domain, *args, **kwargs):
        if not self.env.su and self.env.user.has_group('grn_shakti.group_qc_status_user'):
            has_id_leaf = any(
                isinstance(leaf, (list, tuple)) and len(leaf) == 3
                and leaf[0] == 'id'
                for leaf in domain
            )
            if not has_id_leaf:
                qc_domain = [
                    ('picking_type_id.code', '=', 'incoming'),
                    ('qc_status', '=', 'transfer_to_qc'),
                ]
                domain = expression.AND([domain, qc_domain])
        return super()._search(domain, *args, **kwargs)

    def button_validate(self):
        res = super().button_validate()
        for picking in self:
            if picking.state == 'done':
                picking.qc_status = 'qc_done'
        return res

