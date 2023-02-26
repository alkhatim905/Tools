# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.addons.resource.models.resource import HOURS_PER_DAY
from odoo.exceptions import ValidationError
import datetime


class AccumulateLeaves(models.Model):
    _name = 'accumulate.leaves'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'

    
    def action_paid(self):
        for record in self:
            allocation_obj = self.env['hr.leave.allocation']
            for line in record.lines_ids:
                for leave_line in line.lines_ids:
                    if leave_line.days:
                        data = {}
                        data['employee_id'] = record.employee_id.id
                        data['holiday_type'] = 'employee'
                        data['holiday_status_id'] = leave_line.leave_type_id.id
                        data['name'] = 'ACCUMULATE LEAVE CONCILIATION'

                        if leave_line.leave_type_id.request_unit == 'day':
                            data['number_of_days'] = (leave_line.days * -1)

                        elif leave_line.leave_type_id.request_unit == 'hour':
                            data['number_of_days'] = (leave_line.days * 24 * -1) / (
                                    record.employee_id.resource_calendar_id.hours_per_day or HOURS_PER_DAY)

                        allocation = allocation_obj.sudo().create(data)
                        allocation.action_approve()
            record.state = 'paid'

    name = fields.Char(string='Description', tracking=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('approved', 'Approved'), ('paid', 'Paid'), ('cancel', 'Canceled')],
        default='draft', copy=False, tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True)
    image_medium = fields.Binary(related='employee_id.image_medium')
    lines_ids = fields.One2many('accumulate.leaves.line', 'acc_leaves_id', string='Lines')
    last_accumulate_date = fields.Date(string='Last Accumulate Leave Date', compute='getlast_accumulate_date', store=1)
    accumulate_date = fields.Date('Approved Date')
    total_amount = fields.Float('Total Amount', compute='get_total', store=True)
    total_days = fields.Float('Total Days', compute='get_total', store=True)
    payslip_id = fields.Many2one('hr.payslip', 'Payslip')

    @api.depends('lines_ids', 'lines_ids.days', 'lines_ids.amount')
    def get_total(self):
        for val in self:
            val.total_days = sum([line.days for line in val.lines_ids])
            val.total_amount = sum([line.amount for line in val.lines_ids])

    @api.depends('employee_id')
    def getlast_accumulate_date(self):
        for val in self:
            val.last_accumulate_date = val.employee_id.last_accumulate_date

    def action_confirmed(self):
        for rec in self:
            rec.state = 'confirmed'

    def action_approve(self):
        for rec in self:
            if not rec.accumulate_date:
                rec.accumulate_date = fields.date.today()
            rec.employee_id.last_accumulate_date = fields.date.today()
            rec.state = 'approved'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'


class AccumulateLeaveLines(models.Model):
    _name = 'accumulate.leaves.line'

    acc_leaves_id = fields.Many2one('accumulate.leaves', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string='Employee', related='acc_leaves_id.employee_id')
    contract_id = fields.Many2one('hr.contract', string='Contract')
    amount_rate = fields.Float('Amount')
    lines_ids = fields.One2many('accumulate.leaves.leaves.line', 'leaves_line_id', 'lines')
    days = fields.Float(compute='get_total_days', store=True)
    amount = fields.Float(compute='get_total_days', store=True)

    @api.onchange('employee_id')
    def leaves_line(self):
        lines = []
        for leave in self.env['hr.leave.type'].search([('unpaid', '=', False)]):
            lines.append(
                (0, 0, {
                    'leave_type_id': leave.id,
                }))
        self.lines_ids = lines

    @api.onchange('employee_id')
    def get_contract_id(self):
        self.contract_id = self.employee_id.contract_id.id

    @api.onchange('contract_id')
    def get_amount(self):
        for rec in self:
            rec.amount_rate = rec.contract_id.wage / 30

    
    @api.depends('lines_ids', 'lines_ids.days', 'amount_rate')
    def get_total_days(self):
        for val in self:
            days = 0.0
            for line in val.lines_ids:
                days += line.days
            val.days = days
            amount = (days * val.amount_rate)
            val.amount = round(amount, 2)


class AccumulateLeavesLeaves(models.Model):
    _name = 'accumulate.leaves.leaves.line'

    leaves_line_id = fields.Many2one('accumulate.leaves.line', ondelete='cascade')
    leave_type_id = fields.Many2one('hr.leave.type', 'Leave', domain=[('unpaid', '=', False)])
    days = fields.Float(string='Remaining Days', compute='_compute_leaves', store=True)

    @api.depends('leave_type_id')
    def _compute_leaves(self):
        for val in self:
            data_days = {}
            employee_id = val.leaves_line_id.employee_id.id

            if employee_id:
                data_days = val.leave_type_id.get_days(employee_id)

            result = data_days.get(val.leave_type_id.id, {})

            if val.leave_type_id.request_unit == 'hour':
                val.days = round(result.get('remaining_leaves', 0) / 24, 2)
            else:
                val.days = result.get('remaining_leaves', 0)
