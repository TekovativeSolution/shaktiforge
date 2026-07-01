from odoo import api, models, _
import logging
from pytz import timezone, UTC
import firebase_admin
from firebase_admin import messaging, credentials

_logger = logging.getLogger(__name__)


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to send notification when calendar activity is created"""
        events = super(CalendarEvent, self).create(vals_list)

        for event in events:
            # Send notification to all attendees
            if event.partner_ids:
                for partner in event.partner_ids:
                    if partner.user_ids:
                        for user in partner.user_ids:
                            self._send_calendar_notification(event, user)

        return events

    def write(self, vals):
        """Override write to send notifications when attendees are added"""
        old_partners = {}
        if 'partner_ids' in vals:
            for record in self:
                old_partners[record.id] = record.partner_ids

        result = super(CalendarEvent, self).write(vals)

        # Send notifications to newly added attendees
        if 'partner_ids' in vals:
            for record in self:
                old_partner_list = old_partners.get(record.id, self.env['res.partner'])
                new_partners = record.partner_ids - old_partner_list

                for partner in new_partners:
                    if partner.user_ids:
                        for user in partner.user_ids:
                            self._send_calendar_notification(record, user)

        return result

    def _send_calendar_notification(self, event, user):
        """Send notification for calendar event"""
        try:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            redirect_url = f"{base_url}/web#id={event.id}&model=calendar.event&view_type=form"

            # Format event start time in IST
            formatted_start = 'Not Set'
            if event.start:
                india_tz = timezone('Asia/Kolkata')
                start_utc = event.start.replace(tzinfo=UTC)
                start_ist = start_utc.astimezone(india_tz)
                formatted_start = start_ist.strftime('%d/%m/%Y %H:%M:%S')

            # Format event stop time in IST
            formatted_stop = 'Not Set'
            if event.stop:
                india_tz = timezone('Asia/Kolkata')
                stop_utc = event.stop.replace(tzinfo=UTC)
                stop_ist = stop_utc.astimezone(india_tz)
                formatted_stop = stop_ist.strftime('%d/%m/%Y %H:%M:%S')

            title = f"Calendar Event: {event.name}"
            message_content = f"""
                <p>
                <b>A New Meeting {event.name} is Booked for you:</b><br><br>
                <b>Start Time:</b> {formatted_start}<br>
                <b>End Time:</b> {formatted_stop}<br>
                <b>Summary:</b> {event.description or 'No description'}<br><br>
                <a class='btn btn-primary' href='{redirect_url}' target='_blank'>View Activity</a>
                </p>
            """

            # Send bus notification
            self.env['bus.bus']._sendone(
                user.partner_id,
                'simple_notification',
                {
                    'title': title,
                    'message': message_content,
                    'type': 'info',
                    'sticky': True,
                },
            )

            # Send Firebase push notification
            if user and user.player_lines:
                player_id = user.player_lines[0].player_id
                if player_id:
                    if not firebase_admin._apps:
                        cred_path = '/opt/teknovate/repo/schedule_reminder/models/service-account.json'
                        cred = credentials.Certificate(cred_path)
                        firebase_admin.initialize_app(cred)

                    push_message = f"New Meeting: {event.name}\nStart: {formatted_start}\nEnd: {formatted_stop}\nSummary: {event.description or 'No description'}"
                    fcm_message = messaging.Message(
                        notification=messaging.Notification(
                            title="Calendar Event",
                            body=push_message,
                        ),
                        token=player_id,
                    )
                    try:
                        response = messaging.send(fcm_message)
                        _logger.info(f"FCM Notification sent: {response}")
                    except Exception as e:
                        _logger.error(f"FCM Notification failed: {e}")

            # Post message on event
            post_message = f"""
                <div>
                    <b>Calendar Event Notification</b><br/>
                    Event created for: {user.name}<br/>
                    Start: {formatted_start}<br/>
                    End: {formatted_stop}
                </div>
            """
            event.message_post(body=post_message, message_type="notification")

        except Exception as e:
            _logger.error(f"Error in calendar notification: {e}", exc_info=True)