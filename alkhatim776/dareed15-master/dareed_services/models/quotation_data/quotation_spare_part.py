from odoo import api, fields, models, _


class QuotationSparePart(models.Model):
    _name = "quotation.spare.part"

    name = fields.Char(string="Name")
    name_tr = fields.Char(string="Name Translation")
