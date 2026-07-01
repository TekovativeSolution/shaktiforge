import datetime
from odoo import api, fields, models


class ActivityReminder(models.Model):
    _name = "activity.reminder"
    _description = 'activity reminder'
    _rec_name = "activity"

    activity_type_id = fields.Many2one('mail.activity.type', string="Activity Type")
    summary = fields.Char(string="Summary")
    date_due = fields.Datetime(string="Due Date", index=True, required=True, default=fields.Datetime.now)
    interval_type = fields.Selection([('minutes', 'Minutes'),
                                      ('hours', 'Hours'),
                                      ('days', 'Days')])
    interval_no = fields.Integer(string="Reminder Before")
    send_mail = fields.Boolean(string="Send E-mail Reminder")
    send_sms = fields.Boolean(string="Send SMS Reminder")
    user_id = fields.Many2one('res.users', string="Assigned to")
    is_done = fields.Boolean(string="Done",default=False)
    record_id = fields.Char(string="Record")
    model_name = fields.Char(string='Model')
    reminder_datetime = fields.Datetime(string="Reminder Datetime")
    activity = fields.Integer(string="Mail Activity")



    def _schedule_activity_reminder(self):
        current_time = fields.datetime.now()
        current_time = current_time.strftime("%d/%m/%Y %H:%M")
        records = self.search([('is_done','=',False)])
        for rec in records:
            # if rec.reminder_datetime.strftime("%d/%m/%Y %H:%M") == current_time:
                rec.is_done = True
                lead = self.env[rec.model_name].browse(int(rec.record_id))
                rec.user_id.notify_info(
                    message='Lead: <a href # data-oe-model="crm.lead" data-oe-id={2} target="_blank">{3}<a/> <br/>Activity Type : {0}<br/> Summary : {1}'.format(
                        rec.activity_type_id.name, rec.summary, rec.record_id, lead.name), title="Activity Reminder",
                    sticky=True)
                if rec.send_mail:
                    template = self.env['ir.model.data'].get_object('crm_schedule_reminder',
                                                                    'email_template_crm_activity_reminder')
                    self.env['mail.template'].browse(template.id).send_mail(rec.activity_type_id.id, force_send=True)
                if rec.send_sms and rec.user_id.mobile:
                    sms_message = 'Activity Reminder\n Lead: {2} \n Activity Type : {0}\n Summary : {1}'.format(rec.activity_type_id.name,rec.summary,lead.name)
                    sent_sms = self.env['sms.api'].sudo().hg_send_sms(rec.user_id.mobile,sms_message)
        return

    def _remove_activity_reminders(self):
        activitys = self.search([('is_done', '=', True)])
        if activitys:
            activitys.unlink()
