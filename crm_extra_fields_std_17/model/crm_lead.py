from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError


class CRMLead(models.Model):
    _inherit = "crm.lead"

    contact_person_id = fields.Many2one('res.partner', string="Contact Person",
                                        domain="[('id', 'child_of', partner_id)]")
    cust_type_id = fields.Many2one('customer.type', string="Type of customer")
    product_info_id = fields.Many2one('product.information', string="Product Information")
    l10n_in_gst_treatment = fields.Selection([
        ('regular', 'Registered Business - Regular'),
        ('composition', 'Registered Business - Composition'),
        ('unregistered', 'Unregistered Business'),
        ('consumer', 'Consumer'),
        ('overseas', 'Overseas'),
        ('special_economic_zone', 'Special Economic Zone'),
        ('deemed_export', 'Deemed Export'),
        ('uin_holders', 'UIN Holders'),
    ], string="GST Treatment", store=True, copy=True)
    vat = fields.Char(string="Tax ID")
    # property_account_position_id = fields.Many2one("account.fiscal.position", string="Fiscal Position")

    @api.onchange('contact_person_id')
    def _onchange_contact_person(self):
        if self.contact_person_id:
            self.contact_name = self.contact_person_id.name
            self.partner_name = self.contact_person_id.parent_id.name

    def action_create_partner(self):
        for rec in self:
            partner_ids = self.env["res.partner"]
            partner_obj = partner_ids.search([('name', '=', self.partner_name)])
            if partner_obj:
                raise ValidationError(_('Partner Created'))
            if rec.partner_name:
                comp_obj = partner_ids.create({
                    'name': rec.partner_name,
                    'company_type': 'company',
                    'function': rec.function,
                    'street': rec.street,
                    'street2': rec.street2,
                    'city': rec.city,
                    'state_id': rec.state_id.id,
                    'zip': rec.zip,
                    'country_id': rec.country_id.id,
                    'email': rec.email_from,
                    'mobile': rec.mobile,
                    'website': rec.website,
                    'type': 'contact',
                    'campaign_id': rec.campaign_id.id,
                    'medium_id': rec.medium_id.id,
                    'source_id': rec.source_id.id,
                    'l10n_in_gst_treatment': rec.l10n_in_gst_treatment,
                    'vat': rec.vat,
                    'user_id': rec.user_id.id,
                    'team_id': rec.team_id.id,

                })
                if rec.contact_name:
                    partner_ids.create({
                        'name': rec.contact_name,
                        'company_type': 'person',
                        'street': rec.street,
                        'street2': rec.street2,
                        'city': rec.city,
                        'state_id': rec.state_id.id,
                        'zip': rec.zip,
                        'country_id': rec.country_id.id,
                        'email': rec.email_from,
                        'mobile': rec.mobile,
                        'website': rec.website,
                        'function': self.function,
                        'title': self.title.id,
                        'type': 'contact',
                        'parent_id': comp_obj.id,
                        'campaign_id': rec.campaign_id.id,
                        'medium_id': rec.medium_id.id,
                        'source_id': rec.source_id.id,
                        'l10n_in_gst_treatment': rec.l10n_in_gst_treatment,
                        'vat': rec.vat,
                        'user_id': rec.user_id.id,
                        'team_id': rec.team_id.id,
                    })
            if (not rec.partner_name) and rec.contact_name:
                partner_ids.create({
                    'name': rec.contact_name,
                    'company_type': 'person',
                    'street': rec.street,
                    'street2': rec.street2,
                    'city': rec.city,
                    'state_id': rec.state_id.id,
                    'zip': rec.zip,
                    'country_id': rec.country_id.id,
                    'email': rec.email_from,
                    'mobile': rec.mobile,
                    'website': rec.website,
                    'function': self.function,
                    'title': self.title.id,
                    'type': 'contact',
                    'campaign_id': rec.campaign_id.id,
                    'medium_id': rec.medium_id.id,
                    'source_id': rec.source_id.id,
                    'l10n_in_gst_treatment': rec.l10n_in_gst_treatment,
                    'vat': rec.vat,
                    'user_id': rec.user_id.id,
                    'team_id': rec.team_id.id,
                })


class CustomerType(models.Model):
    _name = "customer.type"

    name = fields.Char(string="Type of customer")


class ProductInformation(models.Model):
    _name = "product.information"

    name = fields.Char(string="Product Information")
