# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class EmployeeKPI(models.Model):
    _name = 'employee.kpi'
    _description = 'Employee KPI'


    name = fields.Char(string='Name', required=1)
    salary_rule_id = fields.Many2one('hr.salary.rule', string='Salary Rule', required=1)


class EmployeeKPIHistory(models.Model):
    _name = 'employee.kpi.history'
    _description = 'Employee KPI History'
    _rec_name = 'employee_id'


    def _get_default_kpi_lines(self):
        kpis = self.env['employee.kpi'].search([])
        lines = []
        if kpis:
            for kpi in kpis:
                lines.append((0, 0, {
                    'employee_kpi_id': kpi.id,
                    'apply': False,
                }))
        if lines:
            return lines
        return False

    kpi_line_ids = fields.One2many('employee.kpi.line', 'employee_kpi_history_id', string="KPI's", default=_get_default_kpi_lines)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=1)
    date = fields.Date(string='Date', required=1)
    month = fields.Integer(compute='get_dates', store=1)
    year = fields.Integer(compute='get_dates', store=1)
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], string='Status', default='draft', copy=False)

    @api.constrains('date', 'month', 'year')
    def _check_dates(self):
        for rec in self:
            count = self.env['employee.kpi.history'].search_count([('month', '=', rec.month), ('year', '=', rec.year)])
            if count > 1:
                raise ValidationError(_('Employee KPI is already added for this month.'))

    
    @api.depends('date')
    def get_dates(self):
        for rec in self:
            if rec.date:
                rec.month = rec.date.month
                rec.year = rec.date.year

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'


class EmployeeKPILine(models.Model):
    _name = 'employee.kpi.line'
    _description = 'Employee KPI Line'
    _rec_name = 'employee_kpi_id'


    employee_kpi_id = fields.Many2one('employee.kpi', string='KPI Config', required=1, ondelete='cascade')
    employee_kpi_history_id = fields.Many2one('employee.kpi.history', string='KPI', required=1, ondelete='cascade')
    apply = fields.Boolean(string='Apply?')