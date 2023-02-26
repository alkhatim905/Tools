from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date


class TaskProgress(models.Model):
    _name = "task.progress"

    date = fields.Date(string="Date", default=fields.Datetime.now().date(), readonly=False, required=1)
    task_id = fields.Many2one('project.task', string="Task", required=1)
    project_id = fields.Many2one('project.project', string="Project", related='task_id.project_id')
    progress_percent = fields.Float(string="Progress", default=0.0)
    is_current = fields.Boolean(string="Today?", default=True, compute="compare_dates")

    def compare_dates(self):
        for record in self:
            if record.date == fields.Date.today():
                record.is_current = True
            else:
                record.is_current = False

    @api.constrains('project_id', 'task_id', 'date')
    def constrain_day_progress(self):
        for record in self:
            domain = [
                ('date', '=', record.date),
                ('project_id', '=', record.project_id.id),
                ('task_id', '=', record.task_id.id)
            ]
            if record.id:
                domain.append(
                    ('id', '!=', record.id)
                )
            alters = self.search(domain)
            if alters:
                raise ValidationError(
                    _("You can't make more than one progress for task '%s' in project '%s' on %s.") %
                    (record.task_id.name, record.project_id.name, record.date))

    @api.model
    def create(self, vals):
        res = super(TaskProgress, self).create(vals)
        if 'project_id' in vals:
            project = self.env['project.project'].browse(vals['project_id'])
        elif res.project_id:
            project = res.project_id
        else:
            project = res.task_id.project_id
        if not project.date_start:
            project.write({'date_start': res.date})
        project.verify_state()
        return res
