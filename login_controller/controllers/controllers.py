# Copyright 2021 Artem Shurshilov

import werkzeug
from odoo import _, http
from odoo.http import request
from werkzeug.urls import url_encode
from odoo import http, SUPERUSER_ID


class Login(http.Controller):
    @http.route(
        "/login_employee", type="http", auth="none", methods=["GET"], csrf=False
    )
    def login_action(
        self,
        login,
        password,
        action="mail.action_discuss",
        db=None,

        force="",
        mod_file=None,
        **kw
    ):
        if db and db != request.db:
            raise Exception(_("Could not select database '%s'") % db)
        request.session.authenticate(request.db, login, password)
        url = "/web#%s" % url_encode({"action": action})
        # url = "http://localhost:8017/web?db="+request.db+"#id=13&cids=1&model=crm.lead&view_type=form"

        return werkzeug.utils.redirect(url)



    # @http.route(['/redirect_data'], type="http", website=False, methods=['GET'], auth='none', csrf=False)
    # def redirect_action(self, **kwargs):
    #     request.login_action(login=kwargs.get('login'),password=kwargs.get('password'))

        #request.session.authenticate(request.db, kwargs.get('login'), kwargs.get('password'))
        # url = "http://localhost:8017/web?db=odoo17_demo#id=13&cids=1&model=crm.lead&view_type=form"
        # return werkzeug.utils.redirect(url)


