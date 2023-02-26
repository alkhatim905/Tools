# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InheritedHRContract(models.Model):
    _inherit = 'hr.contract'

    nationality = fields.Many2one('res.country', string="Nationality", related='employee_id.country_id')
    housing_type = fields.Monetary(string="Housing")
    transport_allowance = fields.Monetary(string="Transportation")
    mobile_allowance = fields.Monetary(string="Mobile")
    other_allowance = fields.Monetary(string="Others")