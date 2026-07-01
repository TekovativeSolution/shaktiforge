from odoo import api, fields, models,_


class ResUsers(models.Model):
    _inherit = 'res.users'

    new_password_temp = fields.Char(string="New Password")