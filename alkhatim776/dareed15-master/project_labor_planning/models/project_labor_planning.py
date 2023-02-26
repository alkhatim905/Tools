# -*- coding: utf-8 -*-

import datetime
from dateutil import relativedelta
import babel.dates

from odoo import api, fields, models, _

# NUMBER_OF_COLS = 31


class ProjectLaborPlanning(models.TransientModel):
    _name = 'project.labor.planning'
    _description = 'Project Labor Planning'

    company_id = fields.Many2one('res.company', string="Company",
                                 default=lambda self: self.env.user.company_id.id, required=True)
    period = fields.Selection([('month', 'Monthly'), ('week', 'Weekly'), ('day', 'Daily')], string="Period")
    project_type = fields.Selection(
        [('cleaning', 'Cleaning And Steam'), ('marble', 'Marble'), ('cleaning_marble', 'Cleaning And Marble')],
        string="Project Type", default='cleaning')
    project_id = fields.Many2one('project.project', string='Project')

    def get_data(self, project):
        result = []
        master_planner_sheet_range = 0
        vacant_no_cleaning_staff = 0
        vacant_no_marble_staff = 0
        plp_config_settings_obj = self.env['plp.config.settings'].search([],limit=1)
        if plp_config_settings_obj:
            master_planner_sheet_range = plp_config_settings_obj.master_planner_sheet_range
            vacant_no_cleaning_staff = plp_config_settings_obj.vacant_no_cleaning_staff
            vacant_no_marble_staff = plp_config_settings_obj.vacant_no_marble_staff
        date = fields.Date.today()
        allocation = 0
        overtime = 0
        project_type = self.project_type
        if project_type == 'cleaning':
            vacant_no_staff = vacant_no_cleaning_staff
        elif project_type == 'marble':
            vacant_no_staff = vacant_no_marble_staff
        else:
            vacant_no_staff = 0
        # Take first day of month or week
        if self.period == 'month':
            date = datetime.date(date.year, date.month, 1)
        elif self.period == 'week':
            date = date - relativedelta.relativedelta(days=date.weekday())
        # Compute others cells
        for p in range(master_planner_sheet_range):
            if self.period == 'month':
                date_to = date + relativedelta.relativedelta(months=1)
                name = date.strftime('%b')
                name = babel.dates.format_date(format="MMM YY", date=date, locale=self._context.get('lang') or 'en_US')
            elif self.period == 'week':
                date_to = date + relativedelta.relativedelta(days=7)
                name = _('Week %s') % babel.dates.format_datetime(
                    date, format="w",
                    locale=self._context.get('lang') or 'en_US'
                )
            else:
                date_to = date + relativedelta.relativedelta(days=1)
                name = babel.dates.format_date(
                    format="EEEE MMM d", date=date, locale=self._context.get('lang') or 'en_US')
            project_allocation_ids = self.env['project.allocation'].search([
                ('date', '>=', date.strftime('%Y-%m-%d')),
                ('date', '<', date_to.strftime('%Y-%m-%d')), ('project_type', '=', project_type),
                ('plp_active', '=', True)
            ])

            if project:
                allocation = sum(
                    project_allocation_ids.filtered(lambda r: r.project_id.id == project.id).mapped('allocation_qty'))
                overtime = sum(
                    project_allocation_ids.filtered(lambda r: r.project_id.id == project.id).mapped('overtime'))
            project_not_attended_ids = self.env['not.attended.staff'].search([
                ('date', '>=', date.strftime('%Y-%m-%d')),
                ('date', '<', date_to.strftime('%Y-%m-%d')), ('project_type', '=', project_type),
            ])
            not_attended_staff = sum(project_not_attended_ids.mapped('not_attended_no'))
            total_allocation_per_day = sum(project_allocation_ids.mapped('allocation_qty'))

            result.append({
                'period': name,
                'project_type': project_type,
                'date': date.strftime('%Y-%m-%d'),
                'date_to': date_to.strftime('%Y-%m-%d'),
                'allocation': allocation,
                'overtime': overtime,
                'not_attended_staff': not_attended_staff,
                'vacant_staff': vacant_no_staff - (not_attended_staff + total_allocation_per_day),
            })
            date = date_to
        return result

    @api.model
    def get_html(self, domain=[]):
        res = self.search([], limit=1)
        plp_config_settings_obj = self.env['plp.config.settings'].search([], limit=1)
        if plp_config_settings_obj:
            master_planner_sheet_range = plp_config_settings_obj.master_planner_sheet_range
        else:
            master_planner_sheet_range = 0

        if not res:
            res = self.create({})
        print('res.project_type',res.project_type)
        domain.append(['plp_active', '=', True])
        domain.append(['project_type', 'in', [res.project_type,'cleaning_marble']])
        projects_list = []
        for x in self.env['project.project'].search(domain):
            res_data = res.get_data(x)
            planned_staff = sum(item['allocation'] for item in res_data)
            overtime = sum(item['overtime'] for item in res_data)
            projects_list.append((x, res_data, planned_staff + overtime))
        rcontext = {
            'projects': projects_list,
            'project_type': res.project_type,
            'periods': res.get_data(project=False),
            'nb_periods': master_planner_sheet_range,
            'company': self.env.user.company_id,
            'format_float': self.env['ir.qweb.field.float'].value_to_html,
        }
        result = {
            'html': self.env.ref('project_labor_planning.project_labor_planning_template').render(rcontext),
            'report_context': {'nb_periods': master_planner_sheet_range, 'period': res.period,
                               'project_type': res.project_type},
        }
        return result
