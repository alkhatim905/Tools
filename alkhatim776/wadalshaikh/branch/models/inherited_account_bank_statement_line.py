# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class account_bank_statement_line(models.Model):

    _inherit = 'account.bank.statement.line'

    @api.model
    def default_get(self, default_fields):
        res = super(account_bank_statement_line, self).default_get(default_fields)
        branch_id = False
        if self._context.get('branch_id'):
            branch_id = self._context.get('branch_id')
        elif self.env.user.branch_id:
            branch_id = self.env.user.branch_id.id
        res.update({
            'branch_id' : branch_id
        })
        return res

    def get_branches_domain(self):
        active_company = self.env['res.company']._company_default_get('account.bank.statement.line')
        branches = self.env['res.branch'].sudo().search([]).filtered(lambda m: m.company_id == active_company)

        domain = [('id', 'in', branches.ids)]
        return domain

    branch_id = fields.Many2one('res.branch', string="Branch", domain=get_branches_domain)
