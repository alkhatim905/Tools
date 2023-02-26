import logging

from odoo import api, exceptions, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ProjectDailyForecast(models.Model):
    _name = 'project.daily.forecast'

    date = fields.Date(string="Date", required=1)
    total_available = fields.Integer(string="Total Available", default=0)
    total_allocated = fields.Integer(string="Total Allocated", compute='_get_workers')
    total_remaining = fields.Integer(string="Total Remaining", compute='_get_workers')

    @api.model
    def create(self, vals):
        res = self.env['project.daily.forecast'].search([('date', '=', vals['date'])])
        if len(res) == 1:
            raise ValidationError(_("There's already a daily forecast for the date: %s" % self.date))
        else:
            return super(ProjectDailyForecast, self).create(vals)

    def write(self, vals):
        if 'date' in vals:
            res = self.env['project.daily.forecast'].search([('date', '=', vals['date'])])
            if len(res) == 1:
                raise ValidationError(_("There's already a daily forecast for the date: %s" % self.date))
        return super(ProjectDailyForecast, self).write(vals)

    def _get_workers(self):
        for record in self:
            sum_cleaning = sum_forecasts = 0
            cleaning_forecasts = self.env['project.forecast.cleaning'].search(
                [('start_date', '=', record.date.strftime('%Y-%m-%d')), ('worker_type', '=', 'basic')])
            marble_forecasts = self.env['project.forecast.marble'].search(
                [('start_date', '=', record.date.strftime('%Y-%m-%d')), ('worker_type', '=', 'basic')])
            sum_cleaning += sum(c.resource_time for c in cleaning_forecasts)
            sum_forecasts += sum(m.resource_time for m in marble_forecasts)
            sum_all = sum_cleaning + sum_forecasts
            record.total_allocated = sum_all
            record.total_remaining = record.total_available - sum_all
