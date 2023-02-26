# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    last_accumulate_date = fields.Date('Last Accumulate Date')
    name_ar = fields.Char('Arabic Name')
    emp_code = fields.Char('Code')
    hiring_date = fields.Date('Hiring Date')
    emp_age = fields.Float(string='Age', compute='get_employee_age')
    emp_exp_years = fields.Integer(string='Years of Experience', compute='get_employee_exp_years')
    emp_exp_months = fields.Integer(string='Months of Experience', compute='get_employee_exp_years')

    @api.depends('birthday')
    def get_employee_age(self):
        today = date.today()
        for rec in self:
            if rec.birthday:
                rec.emp_age = today.year - rec.birthday.year - ((today.month, today.day) < (rec.birthday.month, rec.birthday.day))

    
    @api.depends('experience_ids', 'experience_ids.start_date', 'experience_ids.end_date')
    def get_employee_exp_years(self):
        today = date.today()
        for rec in self:
            total_months = 0
            if rec.experience_ids:
                for line in rec.experience_ids:
                    date_to = line.end_date if line.end_date and line.end_date <= today else today
                    if line.start_date and line.start_date <= today:
                        delta = relativedelta(date_to, line.start_date)
                        full_months = delta.years * 12 + delta.months
                        total_months += full_months
            total_years = int(total_months / 12)
            rec.emp_exp_years = total_years
            rec.emp_exp_months = (total_months - (total_years * 12))

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', '|', '|', '|', ('name', operator, name), ('emp_code', operator, name),
                      ('name_ar', operator, name), ('barcode', operator, name), ('work_email', operator, name)]
        employee = self.search(domain + args, limit=limit)
        return employee.name_get()
