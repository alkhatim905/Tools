from odoo import api, fields, models, _


class QuotationSteamItems(models.Model):
    _name = "quotation.steam.item"

    name = fields.Char(string="Name")
    name_en = fields.Char(string="Name Translation")
