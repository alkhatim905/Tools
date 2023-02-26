# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
import json

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request


class SetBranch(http.Controller):

    @http.route('/set_brnach', type='json', auth="public", methods=['POST'], website=True)
    def custom_hours(self, BranchID, **post):
        user_id = request.env['res.users'].sudo().search([('id', '=', request.env.user.id)])
        user_id.branch_id = BranchID[0]
        return


def branches(companies):
    new_company_data = []
    try:
        for rec in list(companies):
            if rec != ',':
                new_company_data.append(int(rec))
    except:
        new_company_data = request.env.user.branch_ids

    all_branch = request.env['res.branch'].sudo().search([("company_id", "in", new_company_data)])
    return all_branch.ids


def branches_objects(companies):
    new_company_data = []
    try:
        for rec in list(companies):
            if rec != ',':
                new_company_data.append(int(rec))
    except:
        new_company_data = request.env.user.branch_ids

    all_branches = request.env['res.branch'].sudo().search([("company_id", "in", new_company_data)])
    return all_branches


def get_user_branch(companies):
    new_company_data = []
    try:
        for rec in list(companies):
            if rec != ',':
                new_company_data.append(int(rec))
    except:
        new_company_data = request.env.user.branch_ids
    user_branch = 0
    all_branches = request.env['res.branch'].sudo().search([("company_id", "in", new_company_data)])
    if all_branches:
        user_branch += all_branches.sorted()[0].id
    else:
        user_branch += request.env.user.branch_id.id
    return user_branch
