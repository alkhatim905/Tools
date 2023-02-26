from odoo import api, exceptions, fields, models
from datetime import date, datetime, timedelta
from math import ceil


class Project(models.Model):
    _inherit = 'project.project'

    @api.model
    def create(self, vals):
        vals['allow_forecast'] = True
        res = super(Project, self).create(vals)
        if ('is_cleaning_service' in vals and vals['is_cleaning_service']) or \
                ('is_steam_service' in vals and vals['is_steam_service']):
            forecast_basic = self.env['project.forecast.cleaning'].create({
                'employee_id': 1 if not res.user_id.employee else res.user_id.employee_ids[0].id,
                'project_id': res.id,
                'start_date': date.today(),
                'end_date': (datetime.now() + timedelta(days=ceil(res.total_planned_days))).date(),
                'worker_type': 'basic',
                'worker_string': 'Basic Allocated Workers',
            })
            forecast_overtime = self.env['project.forecast.cleaning'].create({
                'employee_id': 1 if not res.user_id.employee else res.user_id.employee_ids[0].id,
                'project_id': res.id,
                'start_date': date.today(),
                'end_date': (datetime.now() + timedelta(days=ceil(res.total_planned_days))).date(),
                'worker_type': 'overtime',
                'worker_string': 'Overtime Allocated Workers',
            })
        if 'is_marble_service' in vals and vals['is_marble_service']:
            forecast_basic = self.env['project.forecast.marble'].create({
                'employee_id': 1 if not res.user_id.employee else res.user_id.employee_ids[0].id,
                'project_id': res.id,
                'start_date': date.today(),
                'end_date': (datetime.now() + timedelta(days=ceil(res.total_planned_days))).date(),
                'worker_type': 'basic',
                'worker_string': 'Basic Allocated Workers',
            })
            forecast_overtime = self.env['project.forecast.marble'].create({
                'employee_id': 1 if not res.user_id.employee else res.user_id.employee_ids[0].id,
                'project_id': res.id,
                'start_date': date.today(),
                'end_date': (datetime.now() + timedelta(days=ceil(res.total_planned_days))).date(),
                'worker_type': 'overtime',
                'worker_string': 'Overtime Allocated Workers',
            })
        return res
