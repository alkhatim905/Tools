from odoo import api, fields, models, _


class HREmployee(models.Model):
    _inherit = "hr.employee"

    is_worker = fields.Boolean(string="Is Worker", default=False)
