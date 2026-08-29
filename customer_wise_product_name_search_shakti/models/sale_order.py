from odoo import api, fields, models, _

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_name_id = fields.Many2one(
        'product.name', 'Customer Product', ondelete='cascade')
    product_code_id = fields.Many2one(
        'product.code', 'Code', ondelete='cascade')
    product_domain = fields.Char(compute="_compute_product_domain")
    product_customer_code_domain = fields.Char(compute="_compute_product_customer_code_domain")

    @api.onchange('product_code_id')
    def _onchange_product_code_id(self):
        for line in self:
            if not line.product_code_id:
                line.product_name_id = False
                line.product_id = False
                line.price_unit = 0.0
                line.name = False
                continue

            domain = [
                ('partner_id', '=', line.order_partner_id.id),
                ('product_code_id', '=', line.product_code_id.id)
            ]
            customer_info = self.env['product.customerinfo'].search(domain, limit=1)

            if customer_info:
                line.product_name_id = customer_info.product_name_id
                line.product_id = customer_info.product_id
                line.price_unit = customer_info.price or 0.0

                desc = ""
                line.set_product_description(customer_info, desc)
                if customer_info.description:
                    line.name += "\n" + customer_info.description
            else:
                line.product_name_id = False
                line.product_id = False
                line.price_unit = 0.0
                line.name = False

    @api.onchange('product_name_id')
    def _onchange_product_name_id(self):
        for line in self:
            if not line.product_name_id:
                line.product_code_id = False
                line.product_id = False
                line.price_unit = 0.0
                line.name = False
                continue

            domain = [
                ('partner_id', '=', line.order_partner_id.id),
                ('product_name_id', '=', line.product_name_id.id)
            ]
            customer_info = self.env['product.customerinfo'].search(domain, limit=1)

            if customer_info:
                line.product_code_id = customer_info.product_code_id
                line.product_id = customer_info.product_id
                line.price_unit = customer_info.price or 0.0

                desc = ""
                line.set_product_description(customer_info, desc)
                if customer_info.description:
                    line.name += "\n" + customer_info.description
            else:
                line.product_code_id = False
                line.product_id = False
                line.price_unit = 0.0
                line.name = False

    @api.depends('order_partner_id')
    def _compute_product_customer_code_domain(self):
        for record in self:
            domain = []

            customer_info_id = self.env['product.customerinfo'].search(
            [('partner_id', '=', record.order_partner_id.id)])
            domain.append(('id', 'in', customer_info_id.mapped('product_code_id').ids))
            record.product_customer_code_domain = str(domain)


    @api.depends('product_name_id','product_code_id')
    def _compute_product_domain(self):
        for record in self:

                domain = []
                flag = False
                if record.product_name_id:
                    customer_info_id = self.env['product.customerinfo'].search([('product_name_id', '=', record.product_name_id.id),('partner_id', '=', record.order_partner_id.id)])
                    domain.append(('id', 'in', customer_info_id.mapped('product_tmpl_id').ids))
                    domain.append(('sale_ok', '=', True))
                    flag = True
                if record.product_code_id and not flag:
                    customer_info_id = self.env['product.customerinfo'].search(
                        [('product_code_id', '=', record.product_code_id.id),
                         ('partner_id', '=', record.order_partner_id.id)])
                    domain.append(('id', 'in', customer_info_id.mapped('product_tmpl_id').ids))
                    domain.append(('sale_ok', '=', True))
                if flag and record.product_code_id:
                    customer_info_id = self.env['product.customerinfo'].search(
                        [('product_name_id', '=', record.product_name_id.id),('product_code_id', '=', record.product_code_id.id),
                         ('partner_id', '=', record.order_partner_id.id)])
                    domain.append(('id', 'in', customer_info_id.mapped('product_tmpl_id').ids))

                record.product_domain = str(domain)

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)

        for line in lines:
            if line.name:
                continue  # already has a description, don't overwrite

            partner_id = line.order_id.partner_id.id
            if not partner_id:
                continue

            domain = [('partner_id', '=', partner_id)]
            if line.product_code_id:
                domain.append(('product_code_id', '=', line.product_code_id.id))
            elif line.product_name_id:
                domain.append(('product_name_id', '=', line.product_name_id.id))
            else:
                continue

            customer_info = self.env['product.customerinfo'].search(domain, limit=1)
            if customer_info:
                desc = ""
                if customer_info.product_code_id:
                    desc += "[%s] " % customer_info.product_code_id.product_code
                if customer_info.product_name_id:
                    desc += customer_info.product_name_id.product_name
                if customer_info.description:
                    desc += "\n" + customer_info.description

                line.write({
                    'product_id': customer_info.product_id.id,
                    'product_name_id': customer_info.product_name_id.id if customer_info.product_name_id else False,
                    'product_code_id': customer_info.product_code_id.id if customer_info.product_code_id else False,
                    'name': desc.strip() or line.product_id.display_name or '/',
                })
            else:
                # fallback so required field is never left blank
                line.name = (
                        line.product_id.display_name
                        or (line.product_code_id.display_name if line.product_code_id else False)
                        or '/'
                )

        return lines
    # @api.model_create_multi
    # def create(self, vals_list):
    #     for vals in vals_list:
    #
    #         if vals.get('product_id'):
    #             continue
    #
    #         partner_id = False
    #         if vals.get('order_id'):
    #             order = self.env['sale.order'].browse(vals['order_id'])
    #             partner_id = order.partner_id.id
    #
    #         if not partner_id:
    #             continue
    #
    #         domain = [('partner_id', '=', partner_id)]
    #
    #         if vals.get('product_name_id'):
    #             domain.append(('product_name_id', '=', vals['product_name_id']))
    #
    #         if vals.get('product_code_id'):
    #             domain.append(('product_code_id', '=', vals['product_code_id']))
    #
    #         customer_info = self.env['product.customerinfo'].search(domain, limit=1)
    #
    #         if customer_info:
    #             vals.update({
    #                 'product_id': customer_info.product_id.id,
    #                 'product_name_id': customer_info.product_name_id.id if customer_info.product_name_id else False,
    #                 'product_code_id': customer_info.product_code_id.id if customer_info.product_code_id else False,
    #                 # 'price_unit': customer_info.price or 0.0,
    #             })
    #
    #             desc = ""
    #             if customer_info.product_code_id:
    #                 desc += "[%s] " % customer_info.product_code_id.product_code
    #             if customer_info.product_name_id:
    #                 desc += customer_info.product_name_id.product_name
    #             if customer_info.description:
    #                 desc += "\n" + customer_info.description
    #
    #             vals['name'] = desc
    #
    #     lines = super().create(vals_list)
    #
    #     for line in lines:
    #         customer_info = self.env['product.customerinfo'].search([
    #             ('partner_id', '=', line.order_partner_id.id),
    #             ('product_id', '=', line.product_id.id),
    #         ], limit=1)
    #
    #         if customer_info:
    #             desc = ""
    #             if customer_info.product_code_id:
    #                 desc += "[%s] " % customer_info.product_code_id.product_code
    #             if customer_info.product_name_id:
    #                 desc += customer_info.product_name_id.product_name
    #             if customer_info.description:
    #                 desc += "\n" + customer_info.description
    #
    #             line.write({
    #                 'product_name_id': customer_info.product_name_id.id if customer_info.product_name_id else False,
    #                 'product_code_id': customer_info.product_code_id.id if customer_info.product_code_id else False,
    #                 # 'price_unit': customer_info.price or 0.0,
    #                 'name': desc,
    #             })
    #
    #     return lines

    def _get_display_price(self):
        """Compute the displayed unit price for a given line.

        Overridden in custom flows:
        * where the price is not specified by the pricelist
        * where the discount is not specified by the pricelist

        Note: self.ensure_one()
        """
        self.ensure_one()

        #####override this method to set customer price list
        customer_info_id = self.env['product.customerinfo'].search(
            [('partner_id', '=', self.order_partner_id.id),('product_tmpl_id','=',self.product_template_id.id)])
        if customer_info_id and customer_info_id.price:
            pricelist_price = customer_info_id.price
        else:
            pricelist_price = self._get_pricelist_price()
        ######

        if self.order_id.pricelist_id.discount_policy == 'with_discount':
            return pricelist_price

        if not self.pricelist_item_id:
            # No pricelist rule found => no discount from pricelist
            return pricelist_price

        base_price = self._get_pricelist_price_before_discount()

        # negative discounts (= surcharge) are included in the display price
        return max(base_price, pricelist_price)


    def set_product_description(self,customer_info_id,desc):
        """To format description of product."""

        if customer_info_id.product_code_id:
            desc += "[" + customer_info_id.product_code_id.product_code + "] "
        if customer_info_id.product_name_id:
            desc +=  customer_info_id.product_name_id.product_name + " "
        self.name = desc





