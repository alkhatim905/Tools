from odoo import api, fields, models, _


class QuotationHousekeepingMaterial(models.Model):
    _name = "quotation.housekeeping.material"

    name = fields.Char(string="Name")
    name_tr = fields.Char(string="Name Translation")
