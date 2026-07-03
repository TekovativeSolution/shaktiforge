# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('state_id')
    def onchange_fiscal_position(self):
        fiscal_positions = self.env['account.fiscal.position'].search([])
        for rec in self:
            if rec.state_id:
                if rec.company_id:
                    if rec.state_id.country_id == rec.company_id.country_id:
                        if rec.state_id == rec.company_id.state_id:
                            rec.property_account_position_id = False
                        else:
                            fiscal_position = fiscal_positions.filtered(lambda fp:fp.name == 'Inter State')
                            rec.property_account_position_id = fiscal_position.id if fiscal_position else False

                    else:
                        fiscal_position = fiscal_positions.filtered(lambda fp: fp.name == 'Export')
                        rec.property_account_position_id = fiscal_position.id if fiscal_position else False
                else:
                    companies = self.env['res.company'].browse(self._context.get('allowed_company_ids'))
                    company = companies[0]
                    if rec.state_id.country_id == company.country_id:
                        if rec.state_id == company.state_id:
                            rec.property_account_position_id = False
                        else:
                            fiscal_position = fiscal_positions.filtered(lambda fp: fp.name == 'Inter State')
                            rec.property_account_position_id = fiscal_position.id if fiscal_position else False
                    else:
                        fiscal_position = fiscal_positions.filtered(lambda fp: fp.name == 'Export')
                        rec.property_account_position_id = fiscal_position.id if fiscal_position else False
