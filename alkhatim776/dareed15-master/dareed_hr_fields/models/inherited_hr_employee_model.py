# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InheritedHREmployee(models.Model):
    _inherit = 'hr.employee'

    issuance_date = fields.Date(string="ID Issuance Date")
    exp_date = fields.Date(string="ID Expiration Date")
    passport_exp_date = fields.Date(string="Passport Expiration Date")
    employee_code = fields.Char(string="Pin Code", store=True)
    dependency_id = fields.Many2one('hr.employee', string="Dependency")
    work_sector_id = fields.Many2one('hr.employee', string="Work Sector")
