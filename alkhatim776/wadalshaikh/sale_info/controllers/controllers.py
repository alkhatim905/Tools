# -*- coding: utf-8 -*-

import json
import logging
from odoo import http
from odoo.http import Controller, dispatch_rpc, request, route
import odoo
import odoo.modules.registry
from odoo.api import call_kw
from odoo.addons.base.models.ir_qweb import render as qweb_render
import requests

_logger = logging.getLogger(__name__)

class PurchaseInfo(http.Controller):
#     @http.route('/purchase_info/purchase_info', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_info/purchase_info/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_info.listing', {
#             'root': '/purchase_info/purchase_info',
#             'objects': http.request.env['purchase_info.purchase_info'].search([]),
#         })

#     @http.route('/purchase_info/purchase_info/objects/<model("purchase_info.purchase_info"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_info.object', {
#             'object': obj
#         })
    @http.route('/point/earns', methods=['post'], type='json', csrf=False , auth='public')
    def point_earn(self, **kw):
        
        params = json.loads(request.httprequest.data);
        patient_id = params['data']['patient_id']

        #patient_id = kw.get('patient_id')
        
        _logger.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Sent batch %s',params )
        if patient_id:
            orders =  request.env['sale.order'].sudo().search(
                [('partner_id', '=', patient_id),('state', '=', 'sale')])
            
            if orders:
              list_of_result = []
              result = {}
              for rec in orders:
                result['usedpoints'] = rec.patient_points_will_get
                result['date']  = rec.confirmation_date
                list_of_result.append(result)

              return {
                    "success": {
                        "code": 0,
                        "message": "patient Earns",
                        "data": list_of_result
                    }
              
                }
                
        
           
            else:
              return {
                "error": {
                    "code": 1060,
                    "message": "No points Earned",
                }
             }