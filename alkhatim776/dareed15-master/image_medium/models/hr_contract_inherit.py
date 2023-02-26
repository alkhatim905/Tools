# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta


class HrContractInherit(models.Model):
    _inherit = 'hr.contract'

    insurance = fields.Float('Insurance')
    tax = fields.Float('Tax')

    @api.onchange('date_start')
    def _onchange_date_start(self):
        if self.date_start:
            self.date_end =  self.date_start + relativedelta(years=1)
            self.trial_date_end =  self.date_start + relativedelta(months=3)
        else:
            self.date_end = False
            self.trial_date_end = False