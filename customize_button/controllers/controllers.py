# -*- coding: utf-8 -*-
# from odoo import http


# class CustomizeButton(http.Controller):
#     @http.route('/customize_button/customize_button', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customize_button/customize_button/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('customize_button.listing', {
#             'root': '/customize_button/customize_button',
#             'objects': http.request.env['customize_button.customize_button'].search([]),
#         })

#     @http.route('/customize_button/customize_button/objects/<model("customize_button.customize_button"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customize_button.object', {
#             'object': obj
#         })

