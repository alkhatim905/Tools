from odoo import api, fields, models, _


class HouseService(models.Model):
    _inherit = "house.service"

    def cancel_project(self):
        if self.project_id:
            project = self.project_id.id
            cleaning_forecasts = self.env['project.forecast.cleaning'].search([('project_id', '=', project)])
            marble_forecasts = self.env['project.forecast.marble'].search([('project_id', '=', project)])
            cleaning_forecasts.unlink()
            marble_forecasts.unlink()
        super(HouseService, self).cancel_project()

    def generate_project(self):
        if self.project_id:
            self.cancel_project()
        super(HouseService, self).generate_project()
