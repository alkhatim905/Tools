# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT

# FIXME QDP TODO need to document all these methods. Please add docstrings

class ProjectAllocation(models.Model):
    _name = 'project.allocation'
    _rec_name = 'project_id'
    _order = 'date'
    _description = 'Project Allocation'

    date = fields.Date('Date', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    project_type = fields.Selection(
        [('cleaning', 'Cleaning And Steam'), ('marble', 'Marble')],
        string="Project Type")
    plp_active = fields.Boolean('Active In Master Planner Sheet', related='project_id.plp_active', store=True)

    allocation_qty = fields.Float('Allocation')
    overtime = fields.Float('Overtime')
    project_id_id = fields.Integer('Project ID', related='project_id.id', store=True, readonly=1)

    _sql_constraints = [
        ('date_project_type_uniq', 'unique (date,project_id,project_type)', 'Allocation Already Exist in This Date.')
    ]

    @api.model
    def save_allocation_data(self, project_id=False, project_type=False, quantity=0, date=False, date_to=False, field=None):
        """When the user changes the quantity on the allocation, adapt the existing quantities """
        domain = [('project_type', '=', project_type),('project_id', '=', project_id), ('date', '>=', str(date)), ('date', '<', str(date_to))]
        # project = self.env['project.project'].browse(project_id)

        if field == 'allocation_qty':
            allocations = self.search(domain, order="date")
            qty_period = sum(allocations.mapped('allocation_qty'))
            new_quantity = quantity - qty_period
            if allocations:
                allocations[0].write({'allocation_qty': allocations[0].allocation_qty + new_quantity})
            else:
                self.create({'date': date, 'project_id': project_id, 'allocation_qty': new_quantity, 'project_type': project_type})

        if field == 'overtime':
            allocations = self.search(domain, order="date")
            qty_period = sum(allocations.mapped('overtime'))
            new_quantity = quantity - qty_period
            if allocations:
                allocations[0].write({'overtime': allocations[0].overtime + new_quantity})
            else:
                self.create({'date': date, 'project_id': project_id, 'overtime': new_quantity, 'project_type': project_type})


class NotAttendedStaff(models.Model):
    _name = 'not.attended.staff'
    _rec_name = 'not_attended_no'
    _order = 'date'
    _description = 'Project Allocation'

    date = fields.Date('Date', required=True)
    project_type = fields.Selection(
        [('cleaning', 'Cleaning And Steam'), ('marble', 'Marble')],
        string="Project Type")
    not_attended_no = fields.Float('Not Attended Number')

    _sql_constraints = [
        ('date_project_type_uniq', 'unique(date, project_type)', 'Date must be unique per project type!'),
    ]

    # @api.model
    # def save_not_attended_data(self, project_type=False, quantity=0, date=False, date_to=False, field=None):
    #     """When the user changes the quantity on the not attended staff, adapt the existing quantities """
    #     domain = [('project_type', '=', project_type), ('date', '>=', str(date)), ('date', '<', str(date_to))]
    #     if field == 'not_attended_staff':
    #         not_attended_ids = self.search(domain, order="date")
    #         qty_period = sum(not_attended_ids.mapped('not_attended_no'))
    #         new_quantity = quantity - qty_period
    #         if not_attended_ids:
    #             not_attended_ids[0].write({'not_attended_no': not_attended_ids[0].not_attended_no + new_quantity})
    #         else:
    #             self.create({'date': date, 'not_attended_no': new_quantity, 'project_type': project_type})