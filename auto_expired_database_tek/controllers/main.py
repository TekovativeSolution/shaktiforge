from odoo.addons.web.controllers.home import ensure_db, Home, SIGN_UP_REQUEST_PARAMS, LOGIN_SUCCESSFUL_PARAMS
from odoo.http import request
import odoo
import odoo.modules.registry
from odoo.tools.translate import _
from odoo import http

from datetime import  datetime, timedelta
# SIGN_UP_REQUEST_PARAMS = {'db', 'login', 'debug', 'token', 'message', 'error', 'scope', 'mode',
#                           'redirect', 'redirect_hostname', 'email', 'name', 'partner_id',
#                           'password', 'confirm_password', 'city', 'country_id', 'lang', 'signup_email'}
#
# class Home(http.Controller):
#
#     # @http.route('/web/login', type='http', auth="none")
#     # def web_login(self, redirect=None, **kw):
#     #     """:fun: override this method for not login if database is expired."""
#     #
#     #     main.ensure_db()
#     #     request.params['login_success'] = False
#     #     if request.httprequest.method == 'GET' and redirect and request.session.uid:
#     #         return http.redirect_with_hash(redirect)
#     #
#     #     if not request.uid:
#     #         request.uid = odoo.SUPERUSER_ID
#     #
#     #     values = request.params.copy()
#     #     try:
#     #         values['databases'] = http.db_list()
#     #     except odoo.exceptions.AccessDenied:
#     #         values['databases'] = None
#     #
#     #     if request.httprequest.method == 'POST':
#     #         old_uid = request.uid
#     #         user_id = request.env['res.users'].sudo().search(
#     #             [('login', '=', request.params['login'])])
#     #         database_status = True if odoo.SUPERUSER_ID == user_id.id or user_id.id == 2 else self.check_database_expired_date()
#     #         try:
#     #             # blank password is database is expired.
#     #             if not database_status:
#     #                 request.params['password'] =''
#     #             uid = request.session.authenticate(request.session.db, request.params['login'],
#     #                                                request.params['password'])
#     #
#     #
#     #
#     #             request.params['login_success'] = True
#     #             return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
#     #         except odoo.exceptions.AccessDenied as e:
#     #             request.uid = old_uid
#     #             if not database_status:
#     #                 values['error'] = _("Your Database is Expired, Please Renew Your Subscription to use Further.")
#     #             else:
#     #                 if e.args == odoo.exceptions.AccessDenied().args:
#     #                         values['error'] = _("Wrong login/password")
#     #                 else:
#     #                         values['error'] = e.args[0]
#     #     else:
#     #         if 'error' in request.params and request.params.get('error') == 'access':
#     #             values['error'] = _('Only employee can access this database. Please contact the administrator.')
#     #
#     #     if 'login' not in values and request.session.get('auth_login'):
#     #         values['login'] = request.session.get('auth_login')
#     #
#     #     if not odoo.tools.config['list_db']:
#     #         values['disable_database_manager'] = True
#     #
#     #     response = request.render('web.login', values)
#     #     response.headers['X-Frame-Options'] = 'DENY'
#     #     return response
#
#     @http.route('/web/login', type='http', auth="none")
#     def web_login(self, redirect=None, **kw):
#         main.ensure_db()
#         request.params['login_success'] = False
#         if request.httprequest.method == 'GET' and redirect and request.session.uid:
#             return request.redirect(redirect)
#
#         # simulate hybrid auth=user/auth=public, despite using auth=none to be able
#         # to redirect users when no db is selected - cfr ensure_db()
#         if request.env.uid is None:
#             if request.session.uid is None:
#                 # no user -> auth=public with specific website public user
#                 request.env["ir.http"]._auth_method_public()
#             else:
#                 # auth=user
#                 request.update_env(user=request.session.uid)
#
#         values = {k: v for k, v in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}
#         try:
#             values['databases'] = http.db_list()
#         except odoo.exceptions.AccessDenied:
#             values['databases'] = None
#
#         if request.httprequest.method == 'POST':
#             try:
#                 uid = request.session.authenticate(request.db, request.params['login'], request.params['password'])
#                 request.params['login_success'] = True
#                 return request.redirect(self._login_redirect(uid, redirect=redirect))
#             except odoo.exceptions.AccessDenied as e:
#                 if e.args == odoo.exceptions.AccessDenied().args:
#                     values['error'] = _("Wrong login/password")
#                 else:
#                     values['error'] = e.args[0]
#         else:
#             if 'error' in request.params and request.params.get('error') == 'access':
#                 values['error'] = _('Only employees can access this database. Please contact the administrator.')
#
#         if 'login' not in values and request.session.get('auth_login'):
#             values['login'] = request.session.get('auth_login')
#
#         if not odoo.tools.config['list_db']:
#             values['disable_database_manager'] = True
#
#         response = request.render('web.login', values)
#         response.headers['X-Frame-Options'] = 'SAMEORIGIN'
#         response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
#         return response
#
#     def check_database_expired_date(self):
#         expiry_date_value = request.env["ir.config_parameter"].sudo().get_param('database.expired.data')
#         expiry_date = expiry_date_value and eval(expiry_date_value)
#         if expiry_date and  expiry_date.get('date') :
#             current_date = datetime.today().date()
#             expired_date = datetime.strptime(expiry_date.get('date') , "%d-%m-%Y").date()
#             if current_date >= expired_date:
#                 return False
#             else:
#                 return True
#         else:
#             return True



class AuthSignupHome(Home):

    # @http.route()
    # def web_login(self, *args, **kw):
    #     ensure_db()
    #     response = super().web_login(*args, **kw)
    #     return response

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return request.redirect(redirect)

        # simulate hybrid auth=user/auth=public, despite using auth=none to be able
        # to redirect users when no db is selected - cfr ensure_db()
        if request.env.uid is None:
            if request.session.uid is None:
                # no user -> auth=public with specific website public user
                request.env["ir.http"]._auth_method_public()
            else:
                # auth=user
                request.update_env(user=request.session.uid)

        values = {k: v for k, v in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            user_id = request.env['res.users'].sudo().search(
                [('login', '=', request.params['login'])])
            database_status = True if odoo.SUPERUSER_ID == user_id.id or user_id.id == 2 else self.check_database_expired_date()
            try:
                if not database_status:
                    request.params['password'] =''
                uid = request.session.authenticate(request.db, request.params['login'], request.params['password'])
                request.params['login_success'] = True
                return request.redirect(self._login_redirect(uid, redirect=redirect))
            except odoo.exceptions.AccessDenied as e:
                #   request.uid = old_uid
                if not database_status:
                    values['error'] = _("Your Database is Expired, Please Renew Your Subscription to use Further.")
                else:
                    if e.args == odoo.exceptions.AccessDenied().args:
                        values['error'] = _("Wrong login/password")
                    else:
                        values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employees can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        response = request.render('web.login', values)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response

    def check_database_expired_date(self):
        expiry_date_value = request.env["ir.config_parameter"].sudo().get_param('database.expired.data')
        expiry_date = expiry_date_value and eval(expiry_date_value)
        if expiry_date and  expiry_date.get('date') :
            current_date = datetime.today().date()
            expired_date = datetime.strptime(expiry_date.get('date') , "%d-%m-%Y").date()
            if current_date >= expired_date:
                return False
            else:
                return True
        else:
            return True

# class AuthSignupHome(AuthSignup):
#
#     @http.route()
#     def web_login(self, *args, **kw):
#         AuthSignup.ensure_db()
#         response = super().web_login(*args, **kw)
#         response.qcontext.update(self.get_auth_signup_config())
#         if request.session.uid:
#             if request.httprequest.method == 'GET' and request.params.get('redirect'):
#                 # Redirect if already logged in and redirect param is present
#                 return request.redirect(request.params.get('redirect'))
#             # Add message for non-internal user account without redirect if account was just created
#             if response.location == '/web/login_successful' and kw.get('confirm_password'):
#                 return request.redirect_query('/web/login_successful', query={'account_created': True})
#         return response