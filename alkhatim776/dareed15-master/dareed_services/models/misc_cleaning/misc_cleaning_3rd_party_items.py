from odoo import api, fields, models, _


class MiscCleaningThirdPartyItem(models.Model):
    _name = "misc.cleaning.3rd.party.item"

    def get_product_id(self):
        return self.env['product.product'].search([('name', '=', 'Items from 3rd party')], limit=1).id

    # Main Data
    name = fields.Char(string="Items from 3rd party:")
    description = fields.Char(string="Description")
    cost_in_sr = fields.Float(string="Cost in SR")

    product_id = fields.Many2one("product.product", string="Product", default=get_product_id)
    service_id = fields.Many2one("house.service")
