from odoo import api, fields, models, _


class QuotationCleaningItems(models.Model):
    _name = "quotation.cleaning.item"

    name = fields.Char(string="Name")
    name_en = fields.Char(string="Name Translation")
    type = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External')
    ], string="Type", required=True)
