from odoo import api, fields, models, _


class CleaningCustomerType(models.Model):
    _name = "cleaning.customer.type"

    name = fields.Char(string="Name")
    product_id = fields.Many2one("product.product", string="Product")
