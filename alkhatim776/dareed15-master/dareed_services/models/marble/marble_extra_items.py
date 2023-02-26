from odoo import api, fields, models, _


class MarbleExtraItemsSurface(models.Model):
    _name = "marble.extra.items"

    def get_product_id(self):
        return self.env['product.product'].search([('name', '=', 'Marble Extra Item')], limit=1).id

    # Main Data
    name = fields.Char(string="Name")
    description = fields.Char(string="Item Description")
    s_price = fields.Float(string="Selling price in SR")

    product_id = fields.Many2one('product.product', string="Product", default=get_product_id)
    service_id = fields.Many2one("house.service")
