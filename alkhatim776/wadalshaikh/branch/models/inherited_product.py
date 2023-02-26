# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ProductTemplateIn(models.Model):
    _inherit = 'product.template'

    
    @api.model
    def default_get(self, default_fields):
        res = super(ProductTemplateIn, self).default_get(default_fields)
        if self.env.user.branch_id:
            res.update({
                'branch_id' : self.env.user.branch_id.id or False
            })
        return res

    def get_branches_domain(self):
        active_company = self.env['res.company']._company_default_get('product.template')
        branches = self.env['res.branch'].sudo().search([]).filtered(lambda m: m.company_id == active_company)

        domain = [('id', 'in', branches.ids)]
        return domain

    branch_id = fields.Many2one('res.branch', string="Branch", domain=get_branches_domain)
