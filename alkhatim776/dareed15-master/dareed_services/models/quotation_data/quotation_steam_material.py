from odoo import api, fields, models, _


class QuotationSteamMaterial(models.Model):
    _name = "quotation.steam.material"

    name = fields.Char(string="Name")
    name_tr = fields.Char(string="Name Translation")
