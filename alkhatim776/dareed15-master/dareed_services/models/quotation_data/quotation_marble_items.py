from odoo import api, fields, models, _


class QuotationMarbleItems(models.Model):
    _name = "quotation.marble.item"

    name = fields.Char(string="Name")
    name_en = fields.Char(string="Name Translation")
