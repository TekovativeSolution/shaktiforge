from odoo import api, fields, models
from .product_category import SR_FIELD_MAP

TRIGGER_FIELDS = {
    'x_category_id',
    'x_process_code_id',
    'x_size1_id',
    'x_size2_id',
    'x_item_group_id',
    'x_end_connection_id',
    'x_pressure_rating_id',
    'x_sch_id',
    'x_material_grade_id',
    'x_die_code_id',
    'x_customer_code_id',
    'x_additional_process_id',
    'x_fitting_standard_id',
}


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_category_id = fields.Many2one(
        'shakti.category', string='1. Category')

    x_process_code_id = fields.Many2one(
        'shakti.process.code', string='2. Process Code')
    x_size1_id = fields.Many2one(
        'shakti.size1', string='3. Size 1')
    x_size2_id = fields.Many2one(
        'shakti.size2', string='4. Size 2')
    x_item_group_id = fields.Many2one(
        'shakti.item.group', string='5. Item Group')
    x_end_connection_id = fields.Many2one(
        'shakti.end.connection', string='6. End Connection Type')
    x_pressure_rating_id = fields.Many2one(
        'shakti.pressure.rating', string='7. Pressure Rating')
    x_sch_id = fields.Many2one(
        'shakti.sch', string='8. SCH')
    x_material_grade_id = fields.Many2one(
        'shakti.material.grade', string='9. Material Grade')
    x_die_code_id = fields.Many2one(
        'shakti.die.code', string='10. Die Code')
    x_customer_code_id = fields.Many2one(
        'shakti.customer.code', string='11. Customer Specific Code')
    x_additional_process_id = fields.Many2one(
        'shakti.additional.process', string='12. Additional Process')
    x_fitting_standard_id = fields.Many2one(
        'shakti.fitting.standard', string='13. Fitting Standard')

    

    def _compute_name_and_code(self):
        for rec in self:
            if not rec.x_category_id:
                continue
            sr_list = rec.x_category_id.get_ordered_sr_list()
            if not sr_list:
                continue

            name_parts = []
            code_parts = []
            for sr in sr_list:
                field_name = SR_FIELD_MAP.get(sr)
                if not field_name:
                    continue
                master_record = getattr(rec, field_name, False)
                if master_record:
                    if master_record.name and field_name != 'x_category_id':
                        name_parts.append(master_record.name)
                    if master_record.code:
                        code_parts.append(master_record.code)

            update_vals = {}
            if name_parts:
                update_vals['name'] = ' '.join(name_parts)
            if code_parts:
                update_vals['default_code'] = ''.join(code_parts)
            if update_vals:
                super(ProductTemplate, rec).write(update_vals)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.x_category_id and rec.x_category_id.field_sequence:
                rec._compute_name_and_code()
        return records

    def write(self, vals):
        result = super().write(vals)
        if TRIGGER_FIELDS & set(vals.keys()):
            for rec in self:
                if rec.x_category_id and rec.x_category_id.field_sequence:
                    rec._compute_name_and_code()
        return result


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _compute_name_and_code(self):
        for rec in self:
            if not rec.x_category_id:
                continue
            sr_list = rec.x_category_id.get_ordered_sr_list()
            if not sr_list:
                continue
            name_parts = []
            code_parts = []
            for sr in sr_list:
                field_name = SR_FIELD_MAP.get(sr)
                if not field_name:
                    continue
                master_record = getattr(rec, field_name, False)
                if master_record:
                    if master_record.name and field_name != 'x_category_id':
                        name_parts.append(master_record.name)
                    if master_record.code:
                        code_parts.append(master_record.code)
            update_vals = {}
            # Variant-level code only; template name is handled by
            # ProductTemplate._compute_name_and_code()
            if code_parts:
                update_vals['default_code'] = ''.join(code_parts)
            if update_vals:
                super(ProductProduct, rec).write(update_vals)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.x_category_id and rec.x_category_id.field_sequence:
                rec._compute_name_and_code()
        return records

    def write(self, vals):
        result = super().write(vals)
        if TRIGGER_FIELDS & set(vals.keys()):
            for rec in self:
                if rec.x_category_id and rec.x_category_id.field_sequence:
                    rec._compute_name_and_code()
        return result
