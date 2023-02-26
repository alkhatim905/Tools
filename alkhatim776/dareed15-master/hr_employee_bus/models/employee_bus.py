# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class EmployeeBus(models.Model):
    _name = 'employee.bus'
    _rec_name = 'number'

    number = fields.Char(string='Bus No.', required=1)
    line = fields.Char(string='Line')
    employee_ids = fields.Many2many('hr.employee', string='Employees')


class EmployeeBusDelay(models.Model):
    _name = 'employee.bus.delay'
    _rec_name = 'date'

    bus_id = fields.Many2one('employee.bus', string='Bus', required=1)
    date = fields.Date(string='Date', required=1)
    employee_ids = fields.Many2many('hr.employee', string='Employees')


    @api.onchange('bus_id')
    def onchange_bus_id(self):
        employees = []
        if self.bus_id:
            for employee in self.bus_id.employee_ids:
                employees.append(employee.id)
        self.employee_ids = [(6, 0, employees)]


    def action_update_attendance(self):
        for rec in self:
            attendances = self.env['hr.attendance'].search([('employee_id', 'in', rec.employee_ids.ids), ('attend_date', '=', rec.date)])
            if attendances:
                attendances.write({
                    'is_bus_delayed': True
                })