from odoo import fields, models, _


class CRMServiceType(models.Model):
    _name = "crm.service.type"

    name = fields.Char(string="Name")
