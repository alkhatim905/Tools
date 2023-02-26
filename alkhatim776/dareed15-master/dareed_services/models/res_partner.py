from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_governmental = fields.Boolean(string="Is Governmental")
    location_url = fields.Char(string="Location URL")
    company_type = fields.Selection(string='Company Type',
                                    selection=[('person', 'Individual'), ('company', 'Company'),
                                               ('government', 'Governmental')])

    @api.depends('is_company')
    def _compute_company_type(self):
        for partner in self:
            partner.company_type = 'company' if partner.is_company else (
                'government' if partner.is_governmental else 'person')

    @api.onchange('company_type')
    def _write_company_type(self):
        for partner in self:
            if partner.company_type == 'company':
                partner.is_governmental = False
                partner.is_company = partner.company_type == 'company'
            elif partner.company_type == 'government':
                partner.is_governmental = partner.company_type == 'government'
                partner.is_company = False
            else:
                partner.is_governmental = False
                partner.is_company = False
