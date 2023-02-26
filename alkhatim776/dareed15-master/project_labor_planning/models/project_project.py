# -*- coding: utf-8 -*-

from odoo import api, fields, models
from math import ceil
from odoo.osv import expression


class ProjectProject(models.Model):
    _inherit = 'project.project'

    plp_active = fields.Boolean('Available In Master Planner Sheet', default=True)
    project_type = fields.Selection(
        [('cleaning', 'Cleaning'), ('marble', 'Marble'), ('cleaning_marble', 'Cleaning And Marble')],
        string="Project Type", compute='_get_project_type', store=True)
    project_allocation_ids = fields.One2many('project.allocation', 'project_id', string='Project Allocations')

    allocated_cleaning_basic_workers = fields.Float(string="Allocated Cleaning Basic Workers",
                                                    compute="_get_allocated_basic_workers")
    allocated_marble_basic_workers = fields.Float(string="Allocated Marble Basic Workers",
                                                  compute="_get_allocated_basic_workers")
    allocated_basic_workers = fields.Float(string="Allocated Basic Workers", compute="_get_allocated_basic_workers")

    allocated_cleaning_overtime_workers = fields.Float(string="Allocated Cleaning Overtime Workers",
                                                       compute="_get_allocated_overtime_workers")
    allocated_marble_overtime_workers = fields.Float(string="Allocated Marble Overtime Workers",
                                                     compute="_get_allocated_overtime_workers")
    allocated_overtime_workers = fields.Float(string="Allocated Overtime Workers",
                                              compute="_get_allocated_overtime_workers")

    total_cleaning_allocated_workers = fields.Float(string="Total Cleaning Allocated Workers",
                                                    compute="_get_total_allocated_workers")
    total_marble_allocated_workers = fields.Float(string="Total Marble Allocated Workers",
                                                  compute="_get_total_allocated_workers")
    total_allocated_workers = fields.Float(string="Total Allocated Workers", compute="_get_total_allocated_workers")

    total_cleaning_remaining_workers = fields.Float(string="Total Cleaning Remaining Workers", compute="_get_total_remaining_workers")
    total_marble_remaining_workers = fields.Float(string="Total Marble Remaining Workers", compute="_get_total_remaining_workers")
    total_remaining_workers = fields.Float(string="Total Remaining Workers", compute="_get_total_remaining_workers")

    total_cleaning_estimated_workers = fields.Float(string="Total Cleaning Estimated Workers", compute='get_planned_hours')
    total_marble_estimated_workers = fields.Float(string="Total Marble Estimated Workers", compute='get_planned_hours')
    total_estimated_workers = fields.Float(string="Total Estimated Workers", compute='get_planned_hours')

    def get_planned_hours(self):
        for project in self:
            # super(ProjectProject, self).get_planned_hours()
            if project.service_id:
                if project.is_cleaning_service or project.is_steam_service:
                    hours_cleaning = project.service_id.hours_of_steam_total + project.service_id.hours_of_cleaning_total
                    project.total_cleaning_estimated_workers = ceil(hours_cleaning / 8)
                    hours_marble = 0
                    project.total_marble_estimated_workers = ceil(hours_marble / 8)
                if project.is_marble_service:
                    hours_cleaning = 0
                    project.total_cleaning_estimated_workers = ceil(hours_cleaning / 8)
                    hours_marble = project.service_id.hours_of_marble_total
                    project.total_marble_estimated_workers = ceil(hours_marble / 8)
                project.total_estimated_workers = project.total_marble_estimated_workers \
                                                  + project.total_cleaning_estimated_workers

    def _get_allocated_basic_workers(self):
        for rec in self:
            allocated_cleaning_basic_workers = sum([allocation.allocation_qty for allocation in
                                                    rec.project_allocation_ids.filtered(
                                                        lambda a: a.project_type == 'cleaning')])
            allocated_marble_basic_workers = sum([allocation.allocation_qty for allocation in
                                                  rec.project_allocation_ids.filtered(
                                                      lambda a: a.project_type == 'marble')])
            rec.allocated_cleaning_basic_workers = allocated_cleaning_basic_workers
            rec.allocated_marble_basic_workers = allocated_marble_basic_workers
            rec.allocated_basic_workers = allocated_cleaning_basic_workers + allocated_marble_basic_workers

    def _get_allocated_overtime_workers(self):
        for rec in self:
            allocated_cleaning_overtime_workers = sum(
                [allocation.overtime for allocation in rec.project_allocation_ids.filtered(
                    lambda a: a.project_type == 'cleaning')])
            allocated_marble_overtime_workers = sum(
                [allocation.overtime for allocation in rec.project_allocation_ids.filtered(
                    lambda a: a.project_type == 'marble')])
            rec.allocated_cleaning_overtime_workers = allocated_cleaning_overtime_workers
            rec.allocated_marble_overtime_workers = allocated_marble_overtime_workers
            rec.allocated_overtime_workers = allocated_cleaning_overtime_workers + allocated_marble_overtime_workers

    def _get_total_allocated_workers(self):
        for rec in self:
            rec.total_cleaning_allocated_workers = rec.allocated_cleaning_basic_workers + rec.allocated_cleaning_overtime_workers
            rec.total_marble_allocated_workers = rec.allocated_marble_basic_workers + rec.allocated_marble_overtime_workers
            rec.total_allocated_workers = rec.allocated_basic_workers + rec.allocated_overtime_workers

    def _get_total_remaining_workers(self):
        for rec in self:
            rec.total_cleaning_remaining_workers = rec.total_cleaning_estimated_workers - rec.total_cleaning_allocated_workers
            rec.total_marble_remaining_workers = rec.total_marble_estimated_workers - rec.total_marble_allocated_workers
            rec.total_remaining_workers = rec.total_estimated_workers - rec.total_allocated_workers

    @api.depends('is_cleaning_service', 'is_steam_service', 'is_marble_service')
    def _get_project_type(self):
        for rec in self:
            project_type = False
            if (rec.is_cleaning_service or rec.is_steam_service) and rec.is_marble_service:
                project_type = 'cleaning_marble'

            if rec.is_cleaning_service or rec.is_steam_service:
                project_type = 'cleaning'

            if rec.is_marble_service:
                project_type = 'marble'
            rec.project_type = project_type

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        project_ids = []
        if name:
            project_ids = self._search(['|',('name', '=', name),('id', operator, name)] + args, limit=limit, access_rights_uid=name_get_uid)
        if not project_ids:
            project_ids = self._search(['|',('name', operator, name),('id', operator, name)] + args, limit=limit, access_rights_uid=name_get_uid)
        return self.browse(project_ids).name_get()
