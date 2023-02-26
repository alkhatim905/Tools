from odoo import api, fields, models, _


class QuotationMarbleMaterial(models.Model):
    _name = "quotation.marble.material"

    name = fields.Char(string="Name")
    name_tr = fields.Char(string="Name Translation")
