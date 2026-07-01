# -*- coding: utf-8 -*-
from odoo import api, fields
from odoo import http, SUPERUSER_ID
from odoo.http import request, Response
import json
import logging
_logger = logging.getLogger(__name__)
from werkzeug.urls import url_encode
import werkzeug

class ResUsersAPI(http.Controller):



    @http.route(['/users'], type="http", website=False, methods = ['GET'], auth='none', csrf=False)
    def res_users_player_create(self, **kwargs):
        if kwargs:

            player_id = request.env['ir.model'].with_user(SUPERUSER_ID).search([('model', '=', 'res.users.player')])
            if player_id:
                user_id = request.env['res.users'].with_user(SUPERUSER_ID).search([('login','=',kwargs.get('login')),('new_password_temp','=',kwargs.get('password'))])
                if not user_id:
                    return json.dumps({
                        "responseCode": 403,
                        "responseMessage": "Please enter correct login or password."})

                if not kwargs.get('player_id'):
                    return json.dumps({
                        "responseCode": 402,
                        "responseMessage": "Token not generated."})

                # delete the existing playerID
                existing_player = request.env['res.users.player'].with_user(SUPERUSER_ID).search([('user_id', '=', user_id.id)])
                if existing_player:
                    existing_player.unlink()
                player_vals = {
                    'player_id': kwargs.get('player_id'),
                    'user_id': user_id.id,
                   # 'password':kwargs.get('password')
                }

                player_id = request.env['res.users.player'].with_user(SUPERUSER_ID).create(player_vals)
                if player_id:
                    user_id.with_user(SUPERUSER_ID).write({'player_lines':[(4, line.id) for line in
                                                    user_id.player_lines]})
                    url = request.env['ir.config_parameter'].with_user(SUPERUSER_ID).get_param('web.base.url')

                    return json.dumps({
                        "responseCode":200,
                        "responseMessage":"Success",
                        'data': {
                            'userId': user_id.id,
                            'userName': user_id.login,
                            'hostUrl':url+'/web/login',
                            'db_list':http.db_list()
                        }
                    })
                else:
                    return '{Status: Fail, Error: Please send some correct data}'
            else:
                return json.dumps({
                    "responseCode": 401,
                    "responseMessage": "You are not registered in our application. Please contact the company.",})
        return '{Status: Fail, Error: Please send some data}'

    @http.route(['/db'], type="http", website=False, methods=['GET'], auth='none', csrf=False)
    def prepare_database_list(self, **kwargs):
        return json.dumps({
            "responseCode": 200,
            "responseMessage": "Success",
            'data': {
                'db_list': http.db_list()
            }
        })

    # @http.route(['/data'], type="http", website=False, methods=['GET'], auth='none', csrf=False)
    # def redirect_action(self, **kwargs):
    #
    #     request.session.authenticate(request.db, kwargs.get('login'), kwargs.get('password'))
    #     url = "/web#%s" % url_encode({"action": 'mail.action_discuss'})
    #     return werkzeug.utils.redirect(url)
