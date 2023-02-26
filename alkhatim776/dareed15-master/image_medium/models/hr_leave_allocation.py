# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from datetime import date, timedelta
import pytz


class HolidaysAllocation(models.Model):
    """ Allocation Requests Access specifications: similar to leave requests """
    _inherit = "hr.leave.allocation"
    _sql_constraints = [
        ('duration_check', "CHECK (1=1)", "The number of days must be greater than 0."),
    ]


class HrLeaveAllocationInherit(models.Model):
    _inherit = 'hr.leave.allocation'

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
