from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare


class ProjectProject(models.Model):
    _inherit = "project.project"

    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
        ('hold', 'On Hold'),
    ], string="Status", default='new')

    def verify_state(self):
        for project in self:
            if (project.state not in ['hold']) and (project.done_lock is False):
                if float_compare(project.total_progress, 0, precision_rounding=6) == 0:
                    project.write({'state': 'new'})
                    if project.date_end:
                        project.write({'date_end': False})
                elif 0 < project.total_progress < 100:
                    project.write({'state': 'in_progress'})
                    if project.date_end:
                        project.write({'date_end': False})
                elif project.total_progress >= 100:
                    project.write({'state': 'done'})
                    if not project.date_end:
                        project.write({'date_end': fields.Datetime.now().date()})

    total_planned_hours = fields.Float(string="Total Estimated Hours", readonly=0)
    total_remaining_hours = fields.Float(string="Total Remaining Hours", compute='get_remaining_hours')
    total_planned_days = fields.Float(string="Total Estimated Days")
    total_progress = fields.Float(string="Total Progress", compute='get_progress')
    is_cleaning_service = fields.Boolean(string="Cleaning", default=False)
    is_steam_service = fields.Boolean(string="Steam", default=False)
    is_marble_service = fields.Boolean(string="Marble", default=False)
    contracts = fields.Boolean(string="Contracts", default=False)

    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')

    done_lock = fields.Boolean(string="Locked", default=False)

    def action_set_to_done(self):
        for project in self:
            project.done_lock = True
            project.state = 'done'

    def action_set_to_continue(self):
        for project in self:
            project.done_lock = False
            project.verify_state()

    def set_on_hold(self):
        for project in self:
            project.state = 'hold'

    def set_not_on_hold(self):
        for project in self:
            project.state = 'in_progress'

    # def get_planned_hours(self):
    #     for project in self:
    #         total = 0
    #         if project.service_id:
    #             total = project.service_id.hours_of_project_with_risk
    #         project.total_planned_hours = total

    def get_remaining_hours(self):
        for project in self:
            total = 0
            tasks = self.env['project.task'].search([('project_id', '=', project.id), ('parent_id', '=', False)])
            for task in tasks:
                if not task.child_ids:
                    total += task.remaining_hours
                else:
                    for subtask in task.child_ids:
                        total += subtask.remaining_hours
            project.total_remaining_hours = total

    
    def get_progress(self):
        for project in self:
            if project.total_planned_hours:
                project.total_progress = ((project.total_planned_hours - project.total_remaining_hours) /
                                          project.total_planned_hours) * 100
            else:
                project.total_progress = 0
            project.verify_state()

    def write(self, values):
        return super(ProjectProject, self).write(values)
