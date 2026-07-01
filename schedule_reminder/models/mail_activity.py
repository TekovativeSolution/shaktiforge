from odoo import api, fields, models, _
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)
from odoo.tools import format_datetime
from pytz import timezone, UTC
import firebase_admin
from firebase_admin import messaging, credentials


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    date_due = fields.Datetime('Due Date', index=True, required=True, default=fields.Datetime.now)
    interval_type = fields.Selection([('minutes', 'Minutes'),
                                      ('hours', 'Hours'),
                                      ('days', 'Days')], default="minutes")
    interval_number = fields.Integer(string="Reminder Before", default=1)
    sh_date_deadline = fields.Datetime('Reminder Due Date', default=lambda self: fields.Datetime.now())

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to send instant notification only for Meeting type"""
        activities = super(MailActivity, self).create(vals_list)

        for activity in activities:
            # Only send notification for Meeting type activities
            if activity.user_id and activity.activity_type_id and activity.activity_type_id.category == 'meeting':
                self._send_instant_activity_notification(activity)

        return activities

    def write(self, vals):
        """Override write to send notifications only for Meeting type when user is changed"""
        old_users = {}
        if 'user_id' in vals:
            for record in self:
                old_users[record.id] = record.user_id

        result = super(MailActivity, self).write(vals)

        if 'user_id' in vals:
            for record in self:
                old_user = old_users.get(record.id)
                # Only send notification for Meeting type activities
                if record.user_id and record.activity_type_id and record.activity_type_id.name == 'Meeting' and (
                        not old_user or old_user.id != record.user_id.id):
                    self._send_instant_activity_notification(record)

        return result

    def _send_instant_activity_notification(self, activity):
        """Send instant notification when activity is created or reassigned"""
        try:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            redirect_url = f"{base_url}/web#id={activity.res_id}&model={activity.res_model}" if activity.res_id and activity.res_model else f"{base_url}/web#action=mail.mail_activity_menu"

            india_tz = timezone('Asia/Kolkata')
            date_due_utc = activity.date_due.replace(tzinfo=UTC)
            date_due_ist = date_due_utc.astimezone(india_tz)
            formatted_due_date = date_due_ist.strftime('%d/%m/%Y %H:%M:%S')

            activity_type = activity.activity_type_id.name if activity.activity_type_id else 'Activity'

            notif_message = f"""
                <p>
                <b>You have been assigned a new activity:</b><br><br>
                <b>Name:</b> {activity.res_name or 'No Name'}<br>
                <b>Activity Type:</b> {activity_type}<br>
                <b>Summary:</b> {activity.summary or 'No summary'}<br>
                <b>Due Date:</b> {formatted_due_date}<br><br>
                <a class='btn btn-primary' href='{redirect_url}' target='_blank'>View Activity</a>
                </p>
            """

            # Send bus notification
            self.env['bus.bus']._sendone(
                activity.user_id.partner_id,
                'simple_notification',
                {
                    'title': f"New Activity Assigned: {activity_type}",
                    'message': notif_message,
                    'type': 'info',
                    'sticky': True,
                },
            )

            push_message = (
                f"New Activity Assigned\n"
                f"Name: {activity.res_name or 'No Name'}\n"
                f"Activity: {activity_type}\n"
                f"Summary: {activity.summary or 'No summary'}\n"
                f"Due Date: {formatted_due_date}"
            )

            # Send Firebase push notification
            if activity.user_id and activity.user_id.player_lines:
                player_id = activity.user_id.player_lines[0].player_id
                if player_id:
                    if not firebase_admin._apps:
                        cred_path = '/opt/teknovate/repo/schedule_reminder/models/service-account.json'
                        cred = credentials.Certificate(cred_path)
                        firebase_admin.initialize_app(cred)

                    message = messaging.Message(
                        notification=messaging.Notification(
                            title="New Activity Assigned",
                            body=push_message,
                        ),
                        token=player_id,
                    )
                    try:
                        response = messaging.send(message)
                        _logger.info(f"FCM Notification sent for new activity: {response}")
                    except Exception as e:
                        _logger.error(f"FCM Notification failed: {e}")

            _logger.info(f"Instant activity notification sent to {activity.user_id.name}")
        except Exception as e:
            _logger.error(f"Error in instant activity notification: {e}", exc_info=True)

    def _schedule_activity_reminder(self):
        """Scheduled reminder notification (existing functionality)"""
        context = dict(self._context) or {}

        current_date = fields.Datetime.now()
        minutes = int(self.env['ir.config_parameter'].sudo().get_param('reminder_before', 15))
        end_date = current_date + timedelta(minutes=minutes)

        # Handle ALL Activities - send reminder for all activity types
        activity_ids = self.env['mail.activity'].sudo().search([
            ('date_due', '>=', current_date),
            ('date_due', '<=', end_date),
        ])

        for activity_id in activity_ids:
            self._send_activity_notification(activity_id, context)

        # Handle Calendar Events
        event_ids = self.env['calendar.event'].sudo().search([
            ('start', '>=', current_date),
            ('start', '<=', end_date),
        ])

        for event in event_ids:
            self._send_calendar_event_notification(event, context)

    def _send_activity_notification(self, activity_id, context):
        """Send reminder notification for mail.activity (before due date)"""
        message = (
            f"{self.env['ir.config_parameter'].sudo().get_param('web.base.url')}/web#id="
            f"{activity_id.res_id}&model={activity_id.res_model}"
        )
        context.update({'redirect_url': message})

        india_tz = timezone('Asia/Kolkata')
        date_due_utc = activity_id.date_due.replace(tzinfo=UTC)
        date_due_ist = date_due_utc.astimezone(india_tz)
        formatted_due_date = date_due_ist.strftime('%d/%m/%Y %H:%M:%S')

        notif_message = f"""
            <p>
            <b>Name:</b> {activity_id.res_name}<br>
            <b>Activity:</b> {activity_id.activity_type_id.name}<br>
            <b>Summary:</b> {activity_id.summary or ''}<br>
            <b>Due Date:</b> {formatted_due_date}<br>
            <a class='btn btn-primary' href='{message}' target='_blank'>Let's Do It!</a>
            </p>
        """

        self.env['bus.bus']._sendone(
            activity_id.user_id.partner_id,
            'simple_notification',
            {
                'title': f"Activity Reminder ({activity_id.activity_type_id.name})",
                'message': notif_message,
                'type': 'warning',
                'sticky': True,
            },
        )

        push_message = (
            f"Name: {activity_id.res_name}\n"
            f"Activity: {activity_id.activity_type_id.name}\n"
            f"Summary: {activity_id.summary or ''}\n"
            f"Due Date: {formatted_due_date}\n"
            f"Link: {message}"
        )

        if activity_id.user_id and activity_id.user_id.player_lines:
            player_id = activity_id.user_id.player_lines[0].player_id

            if player_id:
                if not firebase_admin._apps:
                    cred_path = '/opt/teknovate/repo/schedule_reminder/models/service-account.json'
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)

                message = messaging.Message(
                    notification=messaging.Notification(
                        title="Activity Reminder",
                        body=push_message,
                    ),
                    token=player_id,
                )
                try:
                    response = messaging.send(message)
                    _logger.info(f"FCM Notification sent: {response}")
                except Exception as e:
                    _logger.error(f"FCM Notification failed: {e}")

        return

    def _send_calendar_event_notification(self, event, context):
        """Send reminder notification for calendar.event"""
        message = (
            f"{self.env['ir.config_parameter'].sudo().get_param('web.base.url')}/web#id="
            f"{event.id}&model=calendar.event"
        )
        context.update({'redirect_url': message})

        india_tz = timezone('Asia/Kolkata')
        date_start_utc = event.start.replace(tzinfo=UTC)
        date_start_ist = date_start_utc.astimezone(india_tz)
        formatted_start = date_start_ist.strftime('%d/%m/%Y %H:%M:%S')

        notif_message = f"""
            <p>
            <b>Meeting:</b> {event.name}<br>
            <b>Start:</b> {formatted_start}<br>
            <a class='btn btn-primary' href='{message}' target='_blank'>Join</a>
            </p>
        """
        push_message = (
            f"Meeting: {event.name}\n"
            f"Activity: {formatted_start}\n"
            f"Link: {message}"
        )

        for attendee in event:
            if attendee.partner_id:
                self.env['bus.bus']._sendone(
                    attendee.partner_id,
                    'simple_notification',
                    {
                        'title': f"Meeting Reminder ({event.name})",
                        'message': notif_message,
                        'type': 'warning',
                        'sticky': True,
                    },
                )
                if attendee.user_id and attendee.user_id.player_lines:
                    player_id = attendee.user_id.player_lines[0].player_id

                    if player_id:
                        if not firebase_admin._apps:
                            cred_path = '/opt/teknovate/repo/schedule_reminder/models/service-account.json'
                            cred = credentials.Certificate(cred_path)
                            firebase_admin.initialize_app(cred)

                        message = messaging.Message(
                            notification=messaging.Notification(
                                title="Meeting Reminder",
                                body=push_message,
                            ),
                            token=player_id,
                        )
                        try:
                            response = messaging.send(message)
                            _logger.info(f"FCM Notification sent: {response}")
                        except Exception as e:
                            _logger.error(f"FCM Notification failed: {e}")

        return

    @api.onchange('date_due', 'interval_type', 'interval_number')
    def _onchange_sh_date_deadline(self):
        if self:
            for rec in self:
                if rec.date_due and rec.interval_number and rec.interval_type:
                    if rec.interval_type == 'minutes':
                        rec.sh_date_deadline = rec.date_due - timedelta(minutes=rec.interval_number)
                    if rec.interval_type == 'hours':
                        rec.sh_date_deadline = rec.date_due - timedelta(hours=rec.interval_number)
                    if rec.interval_type == 'days':
                        rec.sh_date_deadline = rec.date_due - timedelta(days=rec.interval_number)
                    if rec.date_due.date() != rec.date_deadline:
                        rec.date_deadline = rec.date_due

    @api.onchange('activity_type_id')
    def _onchange_activity_type_id(self):
        self.date_due = fields.Datetime.now()