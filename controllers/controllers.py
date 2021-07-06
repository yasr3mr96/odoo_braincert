# -*- coding: utf-8 -*-
from odoo import http

# class OdooBraincert(http.Controller):
#     @http.route('/odoo_braincert/odoo_braincert/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/odoo_braincert/odoo_braincert/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('odoo_braincert.listing', {
#             'root': '/odoo_braincert/odoo_braincert',
#             'objects': http.request.env['odoo_braincert.odoo_braincert'].search([]),
#         })

#     @http.route('/odoo_braincert/odoo_braincert/objects/<model("odoo_braincert.odoo_braincert"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('odoo_braincert.object', {
#             'object': obj
#         })