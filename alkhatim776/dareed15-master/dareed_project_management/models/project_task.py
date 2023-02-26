from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from math import ceil, floor


class ProjectTask(models.Model):
    _inherit = "project.task"

    state = fields.Selection([
        ('new', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string="State", default='new')

    task_sequence = fields.Float(string="Sequence", default=1)

    working_days_to_close = fields.Float(string="Working Days To Close", store=True)

    planned_hours = fields.Float(string="Estimated Hours", store=True)
    remaining_hours = fields.Float(string="Remaining Hours", store=False, compute="get_remaining_hours")
    # progress_float = fields.Float(string="Progress Value", store=True)
    progress = fields.Float(string="Task Progress", compute="get_progress", store=False)

    # subtasks_progress = fields.Boolean(string="validate sub-task progress", compute='validate_subtasks_progress')

    progress_line_ids = fields.One2many('task.progress', 'task_id', string="Progress Lines")
    progress_line_count = fields.Integer(string="Progress Lines Count", compute="get_progress_lines_count")

    def get_progress_lines_count(self):
        for record in self:
            record.progress_line_count = len(record.progress_line_ids)
    # def validate_subtasks_progress(self):
    #     for task in self:
    #         if task.child_ids and task.planned_hours != 0.0:
    #             task.subtasks_progress = True
    #         else:
    #             task.subtasks_progress = False

    
    def get_progress(self):
        for task in self:
            if task.planned_hours != 0.0:
                hours_sum = 0
                if task.child_ids:
                    for sub_task in task.child_ids:
                        for line in sub_task.progress_line_ids:
                            if sub_task.planned_hours:
                                hours_sum += line.progress_percent * sub_task.planned_hours
                else:
                    for line in task.progress_line_ids:
                        if task.planned_hours:
                            hours_sum += line.progress_percent * task.planned_hours
                task.progress = hours_sum/task.planned_hours

    @api.onchange('progress_line_ids')
    def get_remaining_hours(self):
        for task in self:
            task.get_progress()
            if task.planned_hours:
                task.remaining_hours = ((100 - task.progress) * task.planned_hours)/100
            else:
                task.remaining_hours = 0

    @api.model
    @api.constrains('planned_hours')
    def validate_sub_tasks_planned_hours(self):
        for record in self:
            if record.parent_id:
                sum_planned = 0
                for sub_task in record.parent_id.child_ids:
                    sum_planned += sub_task.planned_hours
                if sum_planned > record.parent_id.planned_hours:
                    raise ValidationError(_("Can't exceed the number of planned hours for the parent task: " +
                                            record.parent_id.name))

    def reset_sub_sequences(self, sequence=False):
        children = self.child_ids.sorted(key=lambda child: child.id)
        for index, subtask in enumerate(children):
            subtask.write({'task_sequence': (sequence or 1) + ((index+1)/100)})

    def write(self, vals):
        res = super(ProjectTask, self).write(vals)
        if 'task_sequence' in vals:
            for task in self:
                task.reset_sub_sequences(vals['task_sequence'])
        return res

    @api.model
    def create(self, vals):
        if 'default_parent_id' in self._context:
            parent = self.env['project.task'].browse(self._context['default_parent_id'])
            available = parent.planned_hours - parent.subtask_planned_hours
            available_qty = parent.uom_quantity - sum(child.uom_quantity for child in parent.child_ids)
            available_qty = available_qty if available_qty >= 0 else 0
            vals['planned_hours'] = available
            vals['task_sequence'] = (parent.task_sequence or 1) + (len(parent.child_ids) + 1)/100
            vals['uom_id'] = parent.uom_id and parent.uom_id.id
            vals['uom_quantity'] = available_qty
        res = super(ProjectTask, self).create(vals)
        return res

