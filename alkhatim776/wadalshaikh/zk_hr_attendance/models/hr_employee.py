# -*- coding: utf-8 -*-
####################################
# Author: Bashier Elbashier
# Date: 27th February, 2021
####################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HREmployee(models.Model):
    _inherit = "hr.employee"

    biometric_device_id = fields.Integer("Attendance Device ID")

    @api.constrains('biometric_device_id')
    def check_device_id_uniqueness(self):
        emps_with_id = self.search([('biometric_device_id', '=', self.biometric_device_id)])
        if len(emps_with_id) > 1:
            employees = ', '.join([str(elem) for elem in emps_with_id.mapped('name')])
            raise UserError(_("You cannot set the same device ID for two employees: {}.".
                              format(employees)))
