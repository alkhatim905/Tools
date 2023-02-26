from odoo import api, fields, models, _


class SteamCleaningArabicSeat(models.Model):
    _name = "steam.cleaning.arabic.seat"

    # Main Data
    name = fields.Char(string="Unit:")
    type = fields.Selection([
        ('ceil', 'Ceil'),
        ('floor', 'Floor'),
    ], required=True)
    qty = fields.Float(string="Qty of Unit")
    price = fields.Float(string="Unit price in SR", related='product_id.list_price')
    s_price = fields.Float(string="Selling price in SR", compute='get_selling_price')
    time_in_mins = fields.Float(string="Time (Minutes)", compute='get_time_of_cleaning')

    product_id = fields.Many2one("product.product", string="Product")
    service_id = fields.Many2one("house.service")

    @api.onchange('type')
    def get_product_id(self):
        for record in self:
            if record.type:
                product_id = self.env['product.product'].search([
                    ('name', 'ilike', "Arabic Seat - "+('Ceil' if record.type == 'ceil' else 'Floor'))
                ], limit=1)
                record.product_id = product_id.id

    def get_time_of_cleaning(self):
        for record in self:
            record.time_in_mins = (record.qty * record.product_id.product_uom_qty)

    @api.depends('price')
    def get_selling_price(self):
        for record in self:
            record.s_price = (record.qty * (record.price + 5))
