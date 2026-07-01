from odoo import models, api, exceptions, _

class MailActivity(models.Model):
    _inherit = 'mail.activity'

   # def unlink(self):
    #    if not self.env.user.has_group('base.group_system'):
     #       raise exceptions.UserError(_("Only administrators can cancel activities."))
      #  return super(MailActivity, self).unlink()
