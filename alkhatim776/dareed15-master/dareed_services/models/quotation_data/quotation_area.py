from odoo import api, fields, models, _


class QuotationArea(models.Model):
    _name = "quotation.area"

    name = fields.Char(string="Name")
    name_en = fields.Char(string="Name Translation")
    type = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External')
    ], string="Type", required=True)
