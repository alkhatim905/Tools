from odoo import api, fields, models, _


class SteamCleaningCarpets(models.Model):
    _name = "steam.cleaning.carpets"

    def get_product_id(self):
        return self.env['product.product'].search([
            ('name', 'ilike', "Carpets"),
            # ('level_of_dirt', '=', record.level_of_dirt.id)
        ], limit=1)
    # Main Data
    name = fields.Char(string="Unit:")
    qty = fields.Float(string="Qty of Unit")
    price = fields.Float(string="Unit price in SR", related='product_id.list_price')
    s_price = fields.Float(string="Selling price in SR", compute='get_selling_price')

    time_in_mins = fields.Float(string="Time (Minutes)", compute='get_time_of_cleaning')
    product_id = fields.Many2one("product.product", string="Product", default=get_product_id)
    service_id = fields.Many2one("house.service")

    def get_time_of_cleaning(self):
        for record in self:
            record.time_in_mins = (record.qty * record.product_id.product_uom_qty)

    def get_selling_price(self):
        for record in self:
            record.s_price = (record.qty * record.price)
