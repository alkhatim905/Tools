from odoo import api, fields, models, _


class QuotationTool(models.Model):
    _name = "quotation.tool"

    name = fields.Char(string="Name")
    name_tr = fields.Char(string="Name Translation")
    auto_add = fields.Boolean(string="Auto Add", default=False)
