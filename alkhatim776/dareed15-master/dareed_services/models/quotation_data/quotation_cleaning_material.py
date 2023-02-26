from odoo import api, fields, models, _


class QuotationCleaningMaterial(models.Model):
    _name = "quotation.cleaning.material"

    name = fields.Char(string="Name")
    name_tr = fields.Char(string="Name Translation")
    auto_add = fields.Boolean(string="Auto Add", default=False)
