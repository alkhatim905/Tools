# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
from collections import namedtuple


class HRPayslip(models.Model):
    _inherit = "hr.payslip"

    absence_days = fields.Float('Absence Days')
    absence_amount = fields.Float('Leaves Amount Deduction')
    accumulate_leave_amount = fields.Float('Accumulate Leaves Amount')

    
    def compute_sheet(self):
        for payslip in self:
            payslip.get_absence_days()
            payslip.get_accumulate_leaves()
        super(HRPayslip, self).compute_sheet()

    def get_absence_days(self):
        for rec in self:
            start_date = fields.Date.from_string(rec.date_from)
            end_date = fields.Date.from_string(rec.date_to)
            days = 0
            attendance_days = 0
            absence_days = 0
            leaves_days = 0
            global_leaves_days = 0
            legal_leaves_days = 0
            day_lst = []

            for attendance in rec.employee_id.resource_calendar_id.attendance_ids:
                if dict(attendance._fields['dayofweek'].selection).get(attendance.dayofweek) not in day_lst:
                    day_lst.append(dict(attendance._fields['dayofweek'].selection).get(attendance.dayofweek))

            while start_date <= end_date:
                days += 1
                last_date = rec.date_from + relativedelta(days=+days)

                date = fields.Datetime.from_string(start_date).date()
                if date.strftime("%A") in day_lst:
                    attendance_obj = self.env['hr.attendance'].search(
                        [('employee_id', '=', rec.employee_id.id), ('check_in', '<', last_date),
                         ('check_in', '>=', start_date)])
                    if attendance_obj:
                        attendance_days += 1

                    if not attendance_obj:
                        check_leaves = rec.check_leaves(employee_id=rec.employee_id, date_from=start_date,
                                                        date_to=last_date)
                        if check_leaves:
                            if check_leaves['legal']:
                                legal_leaves_days += check_leaves['legal']

                            elif check_leaves['global']:
                                global_leaves_days += check_leaves['global']

                        else:
                            absence_days += 1
                start_date = last_date

            rec.legal_days = legal_leaves_days
            rec.global_days = global_leaves_days
            rec.attendance_days = attendance_days
            rec.absence_days = abs(absence_days)
            rec.absence_amount = (rec.contract_id.wage / 30) * rec.absence_days

        return {'absence_days': absence_days, 'leaves_days': leaves_days}

    
    def get_accumulate_leaves(self):
        for rec in self:
            accumulate_objs = self.env['accumulate.leaves'].search(
                [('employee_id', '=', rec.employee_id.id), ('accumulate_date', '>=', rec.date_from),
                 ('accumulate_date', '<=', rec.date_to), ('state', '=', 'approved')])
            accumulate_leave_amount = sum([rec.total_amount for rec in accumulate_objs])
            rec.accumulate_leave_amount = accumulate_leave_amount

    
    def action_payslip_done(self):
        res = super(HRPayslip, self).action_payslip_done()
        for rec in self:
            accumulate_objs = self.env['accumulate.leaves'].search(
                [('employee_id', '=', rec.employee_id.id), ('accumulate_date', '>=', rec.date_from),
                 ('accumulate_date', '<=', rec.date_to), ('state', '=', 'approved')])
            for acc in accumulate_objs:
                acc.payslip_id = rec.id
                acc.action_paid()
        return res

    
    def refund_sheet(self):
        res = super(HRPayslip, self).refund_sheet()
        for payslip in self:
            accumulate_objs = self.env['accumulate.leaves'].search([('payslip_id', '=', payslip.id)])
            for acc in accumulate_objs:
                acc.state = 'cancel'
        return res

    
    def check_leaves(self, employee_id, date_from, date_to):
        leave_obj = self.env['hr.leave'].search([('employee_id', '=', employee_id.id), ('state', '=', 'validate')])
        Range = namedtuple('Range', ['start', 'end'])
        global_leave_objs = employee_id.resource_calendar_id.global_leave_ids
        r2 = Range(start=date_from, end=date_from)  # todo >>>>> must start && end date must be equal
        legal_leave = 0
        global_leave = 0

        for leave in leave_obj:
            r1 = Range(start=leave.date_from.date(), end=leave.date_to.date())
            latest_start = max(r1.start, r2.start)
            earliest_end = min(r1.end, r2.end)
            delta = (earliest_end - latest_start).days + 1
            overlap = max(0, delta)
            if overlap > 0:
                legal_leave += 1

        # Todo Check Global Leaves
        for g_leave in global_leave_objs:
            r2 = Range(start=date_from, end=date_from)  # todo >>>>> must start && end date must be equal
            r1 = Range(start=g_leave.date_from.date(), end=g_leave.date_to.date())
            latest_start = max(r1.start, r2.start)
            earliest_end = min(r1.end, r2.end)
            delta = (earliest_end - latest_start).days + 1
            g_overlap = max(0, delta)
            if g_overlap:
                global_leave += 1
        if global_leave or legal_leave:
            return {'global': global_leave, 'legal': legal_leave}
