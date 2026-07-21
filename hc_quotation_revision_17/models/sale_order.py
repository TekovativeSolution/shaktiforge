# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # state = fields.Selection(selection_add=[('review', 'Under Review'), ('approve', 'Reviewed'), ('sent',)])
    rev_sale_id = fields.Many2one('sale.order', string="Revision Of", copy=False)
    src_sale_id = fields.Many2one('sale.order', string="Source Record", copy=False)
    rev_sale_ids = fields.One2many('sale.order', 'rev_sale_id', string="Sale History", copy=False)
    rev_count = fields.Integer(string="Reverse Orders", compute="reversed_order_count", copy=False)
    src_sale_ids = fields.One2many('sale.order', 'src_sale_id', string="Sale History(source)", copy=False)
    org_sale_id = fields.Many2one('sale.order', string="Origin", copy=False, )
    src_count = fields.Integer(string="src Orders", compute="src_order_count", copy=False)
    is_revised = fields.Boolean(string="Is Revised", copy=False)
    # reviewed_by = fields.Many2one('res.users', string="Reviewed By", tracking=True)
    confirm_seq = fields.Char(string="Order Number")

    # adv_percent = fields.Float(string="Advance(%)")
    # ret_percent = fields.Float(string="Retention(%)")
    # is_pi_done = fields.Boolean(string="PI Generated", default=False)
    # pi_amount = fields.Float(string="PI")
    # ti_amount = fields.Float(string="TI")
    # last_ret_amount = fields.Float(string="Retention Amount")

    # def compute_pi_ti_amount(self):
    #     for vals in self:
    #         vals.pi_amount = 0
    #         vals.ti_amount = 0
    #         vals.last_ret_amount = 0
    #         # pi = self.env['proforma.invoice'].search([('sale_order_id', '=', vals.id)])
    #         # if pi:
    #         #     vals.pi_amount = pi.mapped('final_amount')[-1] - pi.mapped('ret_amount')[-1]
    #         #     vals.last_ret_amount = pi.mapped('ret_amount')[-1]
    #         # ti = self.env['account.move'].search([('sale_order_id', '=', vals.id)])
    #         # if ti:
    #         # vals.ti_amount = sum(ti.mapped('amount_untaxed'))
    #         vals.ti_amount =0.0
    #         vals.last_ret_amount =0.0
    #         vals.pi_amount=0.0

    # def action_sent_review(self):
    #     self.state = 'review'
    #
    # def action_order_reject(self):
    #     self.state = 'draft'
    #
    # def action_order_approve(self):
    #     self.state = 'approve'
    #     # self.reviewed_by = self.env.user.id

    def revise_quotation(self):
        new_quote = self.copy()
        self.is_revised = True

        if self.org_sale_id:
            new_quote.org_sale_id = self.org_sale_id.id
        else:
            new_quote.org_sale_id = self.id
        self.src_sale_id = new_quote.id
        self.rev_sale_id = new_quote.id
        new_quote.rev_sale_ids = new_quote.rev_sale_ids + self.rev_sale_ids
        new_quote.name = new_quote.org_sale_id.name + "/R" + str(len(new_quote.rev_sale_ids))
        self.state = 'cancel'
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'views': [(False, 'form')],
            'res_id': new_quote.id,
        }

    @api.depends('rev_sale_ids')
    def reversed_order_count(self):
        self.rev_count = len(self.rev_sale_ids)

    @api.depends('src_sale_ids')
    def src_order_count(self):
        self.src_count = len(self.src_sale_ids)

    # @api.returns('mail.message', lambda value: value.id)
    # def message_post(self, **kwargs):
    #     if self.state == 'approve':
    #         self.state = 'draft'
    #     return super(SaleOrder, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)

    # def action_confirm(self):
    #     res = super(SaleOrder, self).action_confirm()
    #
    #     seq = self.env['ir.sequence'].next_by_code('conf.sale.seq')
    #
    #     self.write({
    #         'confirm_seq': seq or _('New')
    #
    #     })
    #     return res

    def action_quotation_sent_new(self):
        # if self.filtered(lambda so: so.state != 'approve'):
        #     raise UserError(_('Only Approved orders can be marked as sent directly.'))
        # for order in self:
        #     order.message_subscribe(partner_ids=order.partner_id.ids)
        self.write({'state': 'sent'})

    # def generate_proforma_invoice(self):
    #     return {
    #         "name": _("Pro-Forma Invoice"),
    #         "type": "ir.actions.act_window",
    #         "view_type": "form",
    #         "view_mode": "form",
    #         "res_model": "proforma.invoice",
    #         "target": "new",
    #         'context': {'default_sale_order_id': self.id,
    #                     'default_project_id': self.project_ids.id,
    #                     'default_sale_order_value': self.amount_total,
    #                     'default_sale_name': self.name,
    #                     'default_partner_id': self.partner_id.id,
    #                     'default_amount_untaxed': self.amount_untaxed,
    #                     'default_amount_tax': self.amount_tax,
    #                     'default_amount': 'percent',
    #                     'default_percentage': self.adv_percent,
    #                     'default_is_from_sale': True,
    #                     'default_description': (self.order_line[0].name + " - " + "Qty(%s) - " + str(
    #                         self.order_line[0].price_subtotal)) % str(
    #                         self.order_line[0].product_uom_qty)
    #                     }
    #
    #     }

    # def action_view_proforma(self):
    #     proformas = self.env['proforma.invoice'].search([('sale_order_id', '=', self.id)]).ids
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Proforma Invoices',
    #         'view_mode': 'tree,form',
    #         'res_model': 'proforma.invoice',
    #         'domain': [('id', 'in', proformas)],
    #     }
    #
    # def action_view_proforma_invoices(self):
    #     proformas = self.env['account.move'].search([('sale_order_id', '=', self.id)]).ids
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Proforma Invoices',
    #         'view_mode': 'tree,form',
    #         'res_model': 'account.move',
    #         'domain': [('id', 'in', proformas)],
    #     }

# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'
#
#     measurement_type = fields.Selection([('lumpsum', 'Lump Sum'), ('approx', 'Approx'), ('actual', 'Actual')],
#                                         string='Measurement Type')
