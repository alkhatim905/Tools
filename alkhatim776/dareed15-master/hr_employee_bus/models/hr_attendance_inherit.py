# -*- coding: utf-8 -*-

from odoo import models, fields, api
import pytz


class HrAttendanceInherit(models.Model):
    _inherit = 'hr.attendance'

    attend_date = fields.Date(compute='_get_attend_date', store=1)
    is_bus_delayed = fields.Boolean(string='Is bus delayed?', default=False)

    @api.depends('check_in', 'employee_id')
    def _get_attend_date(self):
        for rec in self:
            if rec.employee_id and rec.employee_id.user_id:
                employee_tz = pytz.timezone(rec.employee_id.user_id.tz or self.sudo().env.user.tz or 'UTC')
            else:
                employee_tz = pytz.timezone(self.sudo().env.user.tz or 'UTC')
            dt = pytz.UTC.localize(rec.check_in).astimezone(employee_tz).replace(tzinfo=None)
            rec.attend_date = dt.date()