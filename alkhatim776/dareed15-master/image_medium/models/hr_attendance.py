# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from collections import namedtuple
import pytz


class HrAttendanceInherit(models.Model):
    _inherit = 'hr.attendance'

    @api.model
    def create(self, values):
        res = super(HrAttendanceInherit, self).create(values)
        overtime_obj = self.env['employee.overtime']
        employee_obj = res['employee_id']
        check_out = res['check_out']

        if check_out:
            wsl_day_list = []
            attend_checkout_date = fields.Datetime.from_string(res.check_out)
            user = self.env['res.users'].search([('id', '=', self.env.uid)])
            user_time_zone = pytz.timezone(user.partner_id.tz) or pytz.utc
            user_time_zone_offset = datetime.now(user_time_zone).utcoffset().total_seconds() / 60 / 60
            check_out_hours = (attend_checkout_date + timedelta(hours=user_time_zone_offset)).strftime('%H:%M')
            public_hoilday_obj = res.check_public_hoilday(res.employee_id)

            check_in = fields.Datetime.from_string(res.check_in)
            check_out = fields.Datetime.from_string(res.check_out)
            difference = relativedelta(check_out, check_in)
            days = difference.days
            hours = (days * 24) + difference.hours
            minutes = difference.minutes

            for wsl in employee_obj.resource_calendar_id.attendance_ids:
                # get value selection field
                if dict(wsl._fields['dayofweek'].selection).get(wsl.dayofweek) not in wsl_day_list:
                    wsl_day_list.append(dict(wsl._fields['dayofweek'].selection).get(wsl.dayofweek))

            if not public_hoilday_obj:
                # Todo ---- IN ---- Working schedule line
                if wsl_day_list:
                    if check_out.strftime("%A") in wsl_day_list:
                        h, m = check_out_hours.split(":")
                        act_sign_out = round(float(h) + (float(m) / 60), 2)

                        if act_sign_out > wsl.hour_to:
                            vals = {'employee_id': employee_obj.id,
                                    'reason': 'none',
                                    'expect_sign_out': round(wsl.hour_to, 2),
                                    'attend_id': res.id,
                                    'overtime_type': 'working_days',
                                    'act_sign_out': act_sign_out}
                            overtime_obj.sudo().create(vals)

                    # Todo ---- NOT IN ---- Working schedule
                    if check_out.strftime("%A") not in wsl_day_list:
                        act_sign_out = round(float(hours) + (float(minutes) / 60), 2)
                        if act_sign_out > 0:
                            vals = {'employee_id': employee_obj.id,
                                    'reason': 'none',
                                    'expect_sign_out': False,
                                    'attend_id': res.id,
                                    'overtime_type': 'days_off',
                                    'act_sign_out': round(float(hours) + (float(minutes) / 60), 2)}
                            overtime_obj.sudo().create(vals)

            # Todo -- Public Holiday
            if public_hoilday_obj:
                act_sign_out = round(float(hours) + (float(minutes) / 60), 2)
                if act_sign_out > 0:
                    vals = {'employee_id': employee_obj.id,
                            'reason': 'none',
                            'expect_sign_out': False,
                            'attend_id': res.id,
                            'overtime_type': 'public_holiday',
                            'act_sign_out': act_sign_out}
                    overtime_obj.sudo().create(vals)

        return res

    def check_public_hoilday(self, employee_id):
        for attendance in self:
            if attendance.check_out:
                leave_list = []
                Range = namedtuple('Range', ['start', 'end'])
                leave_objs = employee_id.resource_calendar_id.global_leave_ids
                for leave in leave_objs:
                    r1 = Range(start=leave.date_from, end=leave.date_to)
                    r2 = Range(start=attendance.check_in, end=attendance.check_out)
                    latest_start = max(r1.start, r2.start)
                    earliest_end = min(r1.end, r2.end)
                    delta = (earliest_end - latest_start)
                    delta = round((delta.days * 24 + delta.seconds / 3600), 2)
                    overlap = max(0, delta)
                    if overlap and (leave not in leave_list):
                        leave_list.append(leave)
                return leave_list
