from odoo import fields, models


class ProcessCode(models.Model):
    _name = 'shakti.process.code'
    _description = 'Process Code'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)


class Size1(models.Model):
    _name = 'shakti.size1'
    _description = 'Size 1'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)


class Size2(models.Model):
    _name = 'shakti.size2'
    _description = 'Size 2'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)


class ItemGroup(models.Model):
    _name = 'shakti.item.group'
    _description = 'Item Group'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)


class EndConnection(models.Model):
    _name = 'shakti.end.connection'
    _description = 'End Connection Type'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)


class PressureRating(models.Model):
    _name = 'shakti.pressure.rating'
    _description = 'Pressure Rating'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)


class Sch(models.Model):
    _name = 'shakti.sch'
    _description = 'SCH'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)


class MaterialGrade(models.Model):
    _name = 'shakti.material.grade'
    _description = 'Material Grade'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)


class DieCode(models.Model):
    _name = 'shakti.die.code'
    _description = 'Die Code'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)


class CustomerCode(models.Model):
    _name = 'shakti.customer.code'
    _description = 'Customer Specific Code'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)


class AdditionalProcess(models.Model):
    _name = 'shakti.additional.process'
    _description = 'Additional Process'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)


class FittingStandard(models.Model):
    _name = 'shakti.fitting.standard'
    _description = 'Fitting Standard'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
