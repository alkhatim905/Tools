from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    uom_id = fields.Many2one("uom.uom", string="Unit of Measure")
    uom_quantity = fields.Float(string="Quantity")

    @api.model
    @api.constrains('planned_hours')
    def validate_sub_tasks_planned_hours(self):
        for record in self:
            if record.parent_id:
                sum_qty = 0
                for sub_task in record.parent_id.child_ids:
                    sum_qty += sub_task.uom_quantity
                if sum_qty > record.parent_id.uom_quantity:
                    raise ValidationError(_("Can't exceed the Quantity Planned for the parent task: " +
                                            record.parent_id.name))
