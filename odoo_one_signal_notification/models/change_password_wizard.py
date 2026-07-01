from odoo import api, fields, models, exceptions



class ChangePasswordWixard(models.TransientModel):
    _inherit = 'change.password.user'
    #
    # @api.onchange('new_passwd')
    # def new_password_set(self):
    #     context = dict(self._context) or {}
    #     user_id = context.get('active_id')

    def change_password_button(self):
        context = dict(self._context) or {}
        user_id = self.env['res.users'].browse(context.get('active_id'))
        user_id.sudo().write({'new_password_temp':self.new_passwd})
        res = super(ChangePasswordWixard, self).change_password_button()
        return res



