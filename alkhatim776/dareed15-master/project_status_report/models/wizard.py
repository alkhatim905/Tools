from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProjectStatusReport(models.TransientModel):
    _name = "wizard.project.status.report"
    _description = "Project Status Report"

    project_ids = fields.Many2many('project.project', string="Projects")
    projects_category = fields.Selection([
        ('cleaning', 'Cleaning & Steam'),
        ('marble', 'Marble'),
        ('all', 'All'),
    ], string="Projects Category")

    def export_xls(self):
        self.ensure_one()
        data = dict()
        # if self.projects_category == 'cleaning':
        #     data['projects'] = self.env['project.project'].search([
        #         ('is_cleaning_service', '=', True),
        #         ('is_steam_service', '=', True)
        #     ])
        # elif self.projects_category == 'marble':
        #     data['projects'] = self.env['project.project'].search([
        #         ('is_cleaning_service', '=', True),
        #         ('is_steam_service', '=', True)
        #     ])
        # elif self.projects_category == 'all':
        #     data['projects'] = self.env['project.project'].search([])

        data['projects'] = self.project_ids.ids

        if not data:
            raise ValidationError(_("There is no projects to be reported."))
        return {
            'data': data,
            'type': 'ir.actions.report',
            'report_name': 'project_status_report.report_project_status_excel',
            'report_type': 'xlsx',
            'report_file': "Projects Report.xlsx",
        }
