# -*- coding: utf-8 -*-
# from odoo import http


# class TkkEdn(http.Controller):
#     @http.route('/tkk_edn/tkk_edn', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tkk_edn/tkk_edn/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('tkk_edn.listing', {
#             'root': '/tkk_edn/tkk_edn',
#             'objects': http.request.env['tkk_edn.tkk_edn'].search([]),
#         })

#     @http.route('/tkk_edn/tkk_edn/objects/<model("tkk_edn.tkk_edn"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tkk_edn.object', {
#             'object': obj
#         })

