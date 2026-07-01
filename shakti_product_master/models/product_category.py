from odoo import fields, models

SR_FIELD_MAP = {
    1: 'x_category_id',
    2: 'x_process_code_id',
    3: 'x_size1_id',
    4: 'x_size2_id',
    5: 'x_item_group_id',
    6: 'x_end_connection_id',
    7: 'x_pressure_rating_id',
    8: 'x_sch_id',
    9: 'x_material_grade_id',
    10: 'x_die_code_id',
    11: 'x_customer_code_id',
    12: 'x_additional_process_id',
    13: 'x_fitting_standard_id',
}


class ShaktiCategory(models.Model):
    _name = 'shakti.category'
    _description = 'Shakti Category'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    field_sequence = fields.Char(
        string='Field Sequence',
        help=(
            'Enter Sr. Numbers separated by comma in the order you want '
            'them to appear in the product name and internal reference.\n'
            'Example: 2,3,7,5  →  Size1 Size2 SCH EndConnection\n\n'
            'Sr. Reference:\n'
            '1=Category | 2=Process Code | 3=Size 1 | 4=Size 2 | '
            '5=Item Group | 6=End Connection | 7=Pressure Rating | '
            '8=SCH | 9=Material Grade | 10=Die Code | '
            '11=Customer Code | 12=Additional Process | 13=Fitting Standard'
        ),
    )

    def get_ordered_sr_list(self):
        self.ensure_one()
        result = []
        if not self.field_sequence:
            return result
        for part in self.field_sequence.split(','):
            part = part.strip()
            if part.isdigit():
                sr = int(part)
                if sr in SR_FIELD_MAP:
                    result.append(sr)
        return result
