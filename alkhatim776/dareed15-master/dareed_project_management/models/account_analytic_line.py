from odoo import api, fields, models, _
from math import ceil, floor


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    name = fields.Char('Description', required=True, default="\\")

    @api.depends('unit_amount')
    @api.onchange('unit_amount')
    def _get_duration_rounded(self):
        for line in self:
            number = line.unit_amount
            fraction = number - int(number)
            if fraction > 0.5:
                line.unit_amount = ceil(line.unit_amount)
            elif fraction < 0.5 and fraction != 0.0:
                line.unit_amount = floor(line.unit_amount) + 0.5

