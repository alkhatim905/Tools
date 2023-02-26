from odoo import api, fields, models, _


class HouseService(models.Model):
    _inherit = "house.service"

    lead_id = fields.Many2one("crm.lead", string="Lead")
