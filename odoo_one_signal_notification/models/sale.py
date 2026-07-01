from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import requests
import json
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
from google.oauth2 import service_account
SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']
import google.auth.transport.requests

class mail_activity(models.Model):
    _inherit = 'mail.activity'

    # @api.model
    # def create(self, vals):
    #     res = super(mail_activity, self).create(vals)
    #     if res and res.user_id:
    #         users = res.user_id
    #         config_id = self.env['onesignal.config'].get_config_id()
    #         if config_id:
    #             config_id.send_notification_using_firebase(users, "Activity",
    #                                                        "Hello!, New Activity  is scheduled for you.", res.id)
    #     return res

    def custom_call_compute_state(self):
        self._compute_state()


class res_users(models.Model):
    _inherit = 'res.users'

    player_id = fields.Char(string="Player ID")  # no need of this field.
    player_lines = fields.One2many('res.users.player', 'user_id', string="Player IDs", required=True)

    def update_user_player_id(self, player_id):
        lst = self.sudo().player_lines.mapped('player_id')
        if player_id not in lst:
            self.sudo().write({'player_lines': [(0, 0, {'player_id': player_id})]})
        return True

    def delete_player_id(self, player_id):
        self._cr.execute("""delete from res_users_player where player_id='%s'""" % player_id)
        return True


class res_users_player(models.Model):
    _name = 'res.users.player'

    user_id = fields.Many2one('res.users', string="User ID")
    player_id = fields.Char(string="Player ID")


class onesignal_config(models.Model):
    _name = 'onesignal.config'

    rest_api_key = fields.Char(string="Rest Api Key")
    app_id = fields.Char(string="App ID")

    def get_config_id(self):
        return self.search([], limit=1)



    def send_notification_using_firebase(self, users="", title="", msg=""):
            """Send notification using firebase."""
            if not users:
                return

            if not msg:
                return

            if not self.rest_api_key:
                return

            all_player_ids = users.mapped('player_lines')
            player_ids = all_player_ids.filtered(lambda l: l.player_id).mapped('player_id')

            if not player_ids:
                return


            fcm_payload = {
                "message": {
                    "token": player_ids[0],
                    "notification": {
                        "body": msg,
                        "title": title
                    }
                }
            }


            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self._get_access_token(),
            }
            _logger.info('================================header %s', headers)
            _logger.info('================================fcm_payload %s', fcm_payload)

            response = requests.post("https://fcm.googleapis.com/v1/projects/teknovative-new/messages:send",
                                     headers=headers,
                                     data=json.dumps(fcm_payload))
            _logger.info('================================response %s', response.status_code)

            # try:
            #     response = requests.post("https://fcm.googleapis.com/v1/projects/teknovative-new/messages:send",
            #                              headers=headers,
            #                              data=json.dumps(fcm_payload))
            #     _logger.info('================================response %s', response.status_code)
            #     if not response.status_code == 200:
            #         response_error = "Notification not send Error : {0}".format(response.status_code)
            #         raise UserError(_(response_error))
            # except Exception as e:
            #     error = "Notification not send Error : {0}".format(e)
            #     raise UserError(_(error))

    def _get_access_token(self):
            """Retrieve a valid access token that can be used to authorize requests.

            :return: Access token.
            """

            credentials = service_account.Credentials.from_service_account_file(
                '/opt/teknovate/repo/odoo_one_signal_notification/models/service-account.json', scopes=SCOPES)
            request = google.auth.transport.requests.Request()
            credentials.refresh(request)
            return credentials.token


