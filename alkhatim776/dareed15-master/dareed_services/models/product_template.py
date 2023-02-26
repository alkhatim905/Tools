from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_housekeeping = fields.Boolean(string="Is Housekeeping", default=False)
    is_cleaning = fields.Boolean(string="Is Cleaning", default=False)
    is_cleaning_misc = fields.Boolean(string="Is Cleaning Misc.", default=False)
    is_steam = fields.Boolean(string="Is Steam", default=False)
    is_marble = fields.Boolean(string="Is Marble", default=False)

    level_of_dirt = fields.Many2one('cleaning.level.of.dirtiness', string="Level Of Dirtiness")
    product_uom_qty = fields.Float(string="Time in Minutes", default=1)
