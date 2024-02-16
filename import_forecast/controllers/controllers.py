# -*- coding: utf-8 -*-
# from odoo import http


# class ImportForecast(http.Controller):
#     @http.route('/import_forecast/import_forecast', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/import_forecast/import_forecast/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('import_forecast.listing', {
#             'root': '/import_forecast/import_forecast',
#             'objects': http.request.env['import_forecast.import_forecast'].search([]),
#         })

#     @http.route('/import_forecast/import_forecast/objects/<model("import_forecast.import_forecast"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('import_forecast.object', {
#             'object': obj
#         })
