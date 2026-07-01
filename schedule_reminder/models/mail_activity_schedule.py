# -*- coding: utf-8 -*-
import datetime
from odoo import api, fields, models, exceptions
from odoo.tools import html2plaintext


class MailActivitySchedule(models.TransientModel):
    _inherit = 'mail.activity.schedule'


   # date_deadline = fields.Date('Due Date', index=True, default=fields.Date.context_today)
    date_due = fields.Datetime('Due Date', index=True, required=True, default=fields.Datetime.now)
    interval_type = fields.Selection([('minutes', 'Minutes'),
                                        ('hours', 'Hours'),
                                        ('days', 'Days')], default="minutes")
    interval_number = fields.Integer(string="Reminder Before", default=1)

    def _action_schedule_activities(self):
        context = dict(self._context) or {}
        context.update({'interval_type':self.interval_type,'interval_number':self.interval_number})

        return self._get_applied_on_records().with_context(context).activity_schedule(
            activity_type_id=self.activity_type_id.id,
            summary=self.summary,
            note=self.note,
            user_id=self.activity_user_id.id,
            date_deadline=self.date_due
        )

    def action_close_dialog(self):
        res = super(MailActivitySchedule, self).action_close_dialog()
        if self.res_model not in ['crm.lead','res.partner','sale.order','account.move','project.task','helpdesk.ticket','note.note']:
            return res
        self.date_deadline = self.date_due.date()
        reminder_datetime = self.date_due
        if self.interval_type and self.interval_number:
            if self.interval_type == 'minutes':
                reminder_datetime = self.date_due - datetime.timedelta(minutes=self.interval_number)
            if self.interval_type == 'hours':
                reminder_datetime = self.date_due - datetime.timedelta(hours=self.interval_number)
            if self.interval_type == 'days':
                reminder_datetime = self.date_due - datetime.timedelta(days=self.interval_number)

        vals={
            'interval_type':self.interval_type,
            'interval_no':self.interval_number,
            'user_id':self.user_id.id,
            'activity_type_id':self.activity_type_id.id,
            'summary': html2plaintext(self.note),
            'date_due':self.date_due,
            'model_name':self.res_model,
            'record_id':self.res_id,
            'reminder_datetime':reminder_datetime,
            'activity':self.id,
            'is_done':False,
        }
        reminder_id = self.env['activity.reminder'].search([('activity','=',self.id)])
        if reminder_id:
            reminder_id.write(vals)
        else:
            self.env['activity.reminder'].create(vals)
        records = self.env[self.res_model].search([('id','=',self.res_id)])
        note_datetime = self.date_due + datetime.timedelta(hours=5, minutes=30)
        print(note_datetime)
        message = "<div>Activity Reminder<br/>Activity for {0} on {1} <br/> Assign to: {2}</div>".format(self.activity_type_id.name,note_datetime,self.user_id.name)
        for rec in records:
            rec.message_post(body=message, message_type="notification")
        return res


