from odoo import api, fields, models, _
import time


class MarblePolishingSurface(models.Model):
    _name = "marble.polishing.surface"

    def get_product_id(self):
        return self.env['product.product'].search([
            ('name', 'ilike', 'Polishing of marble base-board')
        ], limit=1)

    # Main Data
    name = fields.Char(string="Surface:")
    linear_m = fields.Float(string="Linear m")
    price = fields.Float(string="Unit price in SR", related='product_id.list_price')
    s_price = fields.Float(string="Selling price in SR", compute='get_selling_price')

    product_id = fields.Many2one("product.product", string="Product", default=get_product_id)
    service_id = fields.Many2one("house.service")
    time_in_hours = fields.Float(string="Time (Hours)", compute='get_time_in_hours')

    @api.depends('price')
    def get_selling_price(self):
        for record in self:
            record.s_price = (record.linear_m * record.price)

    def get_time_in_hours(self):
        for record in self:
            record.time_in_hours = (record.linear_m * record.product_id.product_uom_qty) / 60
