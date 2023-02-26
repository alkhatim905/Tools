from odoo import fields, models, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    service_id = fields.Many2one("house.service", string="Calculation Sheet")
    service_reference = fields.Char("Calculation Sheet Ref.", compute="_get_service_reference", store=True)

    @api.depends('service_id')
    def _get_service_reference(self):
        for project in self:
            if project.service_id:
                service_reference = project.name + ' - '+str(project.service_id.id)
            else:
                service_reference = ''
            project.service_reference = service_reference
