from odoo import api, models,fields ,Command,_


class ResUsers(models.Model):
    _inherit = 'res.users'

    notification_type = fields.Selection([
        ('email', 'Handle by Emails'),
        ('inbox', 'Handle in Software')],
        'Notification', required=True, default='email',
        compute='_compute_notification_type', inverse='_inverse_notification_type', store=True,
        help="Policy on how to handle Chatter notifications:\n"
             "- Handle by Emails: notifications are sent to your email address\n"
             "- Handle in Odoo: notifications appear in your Odoo Inbox")

    ###override this method for changes string name
    @api.depends('share', 'groups_id')
    def _compute_notification_type(self):
        # Because of the `groups_id` in the `api.depends`,
        # this code will be called for any change of group on a user,
        # even unrelated to the group_mail_notification_type_inbox or share flag.
        # e.g. if you add HR > Manager to a user, this method will be called.
        # It should therefore be written to be as performant as possible, and make the less change/write as possible
        # when it's not `mail.group_mail_notification_type_inbox` or `share` that are being changed.
        inbox_group_id = self.env['ir.model.data']._xmlid_to_res_id('mail.group_mail_notification_type_inbox')

        self.filtered_domain([
            ('groups_id', 'in', inbox_group_id), ('notification_type', '!=', 'inbox')
        ]).notification_type = 'inbox'
        self.filtered_domain([
            ('groups_id', 'not in', inbox_group_id), ('notification_type', '=', 'inbox')
        ]).notification_type = 'email'

        # Special case: internal users with inbox notifications converted to portal must be converted to email users
        self.filtered_domain([('share', '=', True), ('notification_type', '=', 'inbox')]).notification_type = 'email'


    def _inverse_notification_type(self):
        inbox_group = self.env.ref('mail.group_mail_notification_type_inbox')
        inbox_users = self.filtered(lambda user: user.notification_type == 'inbox')
        inbox_users.write({"groups_id": [Command.link(inbox_group.id)]})
        (self - inbox_users).write({"groups_id": [Command.unlink(inbox_group.id)]})

