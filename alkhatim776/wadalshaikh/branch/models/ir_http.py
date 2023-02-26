# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import hashlib
import json

import requests
from odoo import api, models, fields
from odoo.http import request
from odoo.tools import ustr
# from odoo.addons.web.controllers.main import module_boot, HomeStaticTemplateHelpers
from odoo.addons.branch.controllers.main import branches, get_user_branch, branches_objects
# from odoo.addons.branch.controllers.main import
# from odoo.addons.branch.controllers.main import
import odoo


def get_showed_companies():
    companies = request.httprequest.cookies.get("cids")

    branch_data = branches(companies)
    print("Switched branch ids", branch_data)
    return branch_data


def branches_objects_data():
    companies = request.httprequest.cookies.get("cids")

    branch_data = branches_objects(companies)
    print("Switched branch branches_objects", branch_data)
    return branch_data


def get_user_current_branch():
    companies = request.httprequest.cookies.get("cids")

    branch_data = get_user_branch(companies)
    print("Switched Current User Branch", branch_data)
    return branch_data


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        """ Add information about iap enrich to perform """
        session_info = super(Http, self).session_info()
        user = request.env.user

        companies = request.httprequest.cookies.get("cids")
        default_companies = user.company_ids

        new_company_data = []
        try:
            for rec in list(companies):
                if rec != ',':
                    new_company_data.append(int(rec))
        except:
            for recs in default_companies:
                new_company_data.append(int(recs))

        all_branch = request.env['res.branch'].sudo().search([("company_id", "in", new_company_data)])
        current_branch = 0
        if all_branch:
            try:
                current_branch += all_branch[0].id
            except:
                current_branch += user.branch_id.id
        else:
            current_branch += user.branch_id.id

        if self.env.user.has_group('base.group_user'):
            session_info.update({
                # current_company should be default_company
                "user_companies": {
                    'current_company': user.company_id.id,
                    'allowed_companies': {
                        comp.id: {
                            'id': comp.id,
                            'name': comp.name,
                        } for comp in user.company_ids
                    },
                },
                "user_branches": {
                    'current_branch': current_branch,
                    'allowed_branches': {
                        comps.id: {
                            'id': comps.id,
                            'name': comps.name,
                        } for comps in all_branch
                    },
                },
                "currencies": self.get_currencies(),
                "show_effect": True,
                # "ammar": user.branch_ids.filtered(lambda branch: branch.company_id in list(all_companies)).ids,
                "ammar": request.env.user.branch_ids.ids,
                "display_switch_company_menu": user.has_group('base.group_multi_company') and len(user.company_ids) > 1,
                "display_switch_branch_menu": user.has_group('branch.group_multi_branch') and len(user.branch_ids) > 1,
                # "cache_hashes": cache_hashes,
                "allowed_branch_ids": all_branch.ids
            })
        return session_info

# class Http(models.AbstractModel):
#     _inherit = 'ir.http'

#     def session_info(self):
#         user = request.env.user
#         version_info = odoo.service.common.exp_version()

#         user_context = request.session.get_context() if request.session.uid else {}

#         session_info = {
#             "uid": request.session.uid,
#             "is_system": user._is_system() if request.session.uid else False,
#             "is_admin": user._is_admin() if request.session.uid else False,
#             "user_context": request.session.get_context() if request.session.uid else {},
#             "db": request.session.db,
#             "server_version": version_info.get('server_version'),
#             "server_version_info": version_info.get('server_version_info'),
#             "name": user.name,
#             "username": user.login,
#             "partner_display_name": user.partner_id.display_name,
#             "company_id": user.company_id.id if request.session.uid else None,  # YTI TODO: Remove this from the user context
#             "branch_id": user.branch_id.id if request.session.uid else None,
#             "partner_id": user.partner_id.id if request.session.uid and user.partner_id else None,
#             "web.base.url": self.env['ir.config_parameter'].sudo().get_param('web.base.url', default=''),
#         }
#         if self.env.user.has_group('base.group_user'):
#             # the following is only useful in the context of a webclient bootstrapping
#             # but is still included in some other calls (e.g. '/web/session/authenticate')
#             # to avoid access errors and unnecessary information, it is only included for users
#             # with access to the backend ('internal'-type users)
#             mods = module_boot()
#             qweb_checksum = HomeStaticTemplateHelpers.get_qweb_templates_checksum(addons=mods, debug=request.session.debug)
#             lang = user_context.get("lang")
#             translation_hash = request.env['ir.translation'].get_web_translations_hash(mods, lang)
#             menu_json_utf8 = json.dumps(request.env['ir.ui.menu'].load_menus(request.session.debug), default=ustr, sort_keys=True).encode()
#             cache_hashes = {
#                 "load_menus": hashlib.sha1(menu_json_utf8).hexdigest(),
#                 "qweb": qweb_checksum,
#                 "translations": translation_hash,
#             }
#             session_info.update({
#                 # current_company should be default_company
#                 "user_companies": {'current_company': (user.company_id.id, user.company_id.name), 'allowed_companies': [(comp.id, comp.name) for comp in user.company_ids]},
#                 "user_branches": {'current_branch': (user.branch_id.id, user.branch_id.name), 'allowed_branch': [(comp.id, comp.name) for comp in user.branch_ids]},
#                 "currencies": self.get_currencies(),
#                 "show_effect": True,
#                 "display_switch_company_menu": user.has_group('base.group_multi_company') and len(user.company_ids) > 1,
#                 "display_switch_branch_menu": user.has_group('branch.group_multi_branch') and len(user.branch_ids) > 1,
#                 "cache_hashes": cache_hashes,
#                 "allowed_branch_ids" : user.branch_id.ids
#             })
#         return session_info

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
