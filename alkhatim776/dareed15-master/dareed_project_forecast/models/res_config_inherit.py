# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    forecast_uom = fields.Selection([
        ('hour', 'Hours'),
        ('day', 'Days'),
    ], string="Dareed Forecast UoM", related='company_id.forecast_uom', required=True, help="Encode your forecasts in hours or days.", readonly=False)
    forecast_span = fields.Selection([
        ('day', 'By day'),
        ('week', 'By week'),
        ('month', 'By month')
    ], string="Dareed Forecast Span", related='company_id.forecast_span', required=True, help="Encode your forecast in a table displayed by days, weeks or the whole year.", readonly=False)
