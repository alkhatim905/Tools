from odoo import api, fields, models, _


class QuotationEquipment(models.Model):
    _name = "quotation.equipment"

    name = fields.Char(string="Name")
    name_tr = fields.Char(string="Name Translation")
