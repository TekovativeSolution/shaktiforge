from odoo import models, fields, api
import mimetypes

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_order_id = fields.Many2one('sale.order', string='Sales Order')
    customer_id = fields.Many2one('res.partner', string='Customer')
    sale_description = fields.Text(string='Product Description')
    attachment = fields.Binary(string='Attachment')
    domain = fields.Char(string="domain")

    @api.onchange('product_id')
    def _onchange_product_id_set_sale_order(self):

        sale_orders = self.env['sale.order'].search([
            ('order_line.product_id', '=', self.product_id.id),
            ('order_line.production_status', '=', 'pending')
        ])

        if sale_orders:
            self.domain = str([('id', 'in', sale_orders.ids)])
        else:
            self.domain = [('id', '=', False)]

    @api.onchange('sale_order_id')
    def _onchange_sale_order_details(self):
        for rec in self:
            sale_line = self.env['sale.order.line'].search([
                ('order_id', '=', rec.sale_order_id.id),
                ('product_id', '=', rec.product_id.id),
            ], limit=1)
            rec.customer_id = rec.sale_order_id.partner_id if rec.sale_order_id else False
            rec.sale_description = sale_line.name if sale_line else ''
            rec.attachment = sale_line.attachment if sale_line else False

    @api.model
    def get_attachment_preview(self, model, field_name, record_id):
        record = self.env[model].browse(record_id)
        if not record.exists():
            return {}

        attachment = self.env['ir.attachment'].search([
            ('res_model', '=', model),
            ('res_field', '=', field_name),
            ('res_id', '=', record_id)
        ], limit=1)

        if attachment:
            mimetype = attachment.mimetype or mimetypes.guess_type(attachment.name)[0]
            is_image = mimetype and mimetype.startswith('image/')
            is_pdf = mimetype == 'application/pdf'
            return {
                'id': attachment.id,
                'name': attachment.name,
                'mimetype': mimetype,
                'url': f'/web/content/{attachment.id}',
                'is_image': is_image,
                'is_pdf': is_pdf,
            }
        return {}

    def _default_show_customer_info(self):
        param_value = self.env['ir.config_parameter'].sudo().get_param('custom.mrp.show_customer_info')
        return param_value == 'True'

    show_customer_info = fields.Boolean(
        string="Show Customer Info",
        compute="_compute_show_customer_info",
        store=True,
        default=_default_show_customer_info
    )

    @api.depends_context('uid')
    def _compute_show_customer_info(self):
        param_value = self.env['ir.config_parameter'].sudo().get_param('custom.mrp.show_customer_info')
        for rec in self:
            rec.show_customer_info = (param_value == 'True')

