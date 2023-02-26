import logging

from odoo import api, exceptions, fields, models, _

_logger = logging.getLogger(__name__)


class ProjectForecastCleaningSteam(models.Model):
    _name = 'project.forecast.marble'
    _inherit = 'planning.slot'

    worker_type = fields.Selection([
        ('basic', 'Basic Allocated Workers'),
        ('overtime', 'Overtime Allocated Workers'),
    ], string="Workers Type")
    worker_string = fields.Char(string="Allocated Workers")

    @api.onchange('worker_type')
    def set_worker_string(self):
        for record in self:
            record.update({'worker_string': dict(record._fields['worker_type'].selection).get(record.worker_type)})