from odoo import api, fields, models, _


class SteamCleaningMattress(models.Model):
    _name = "steam.cleaning.mattress"

    # Main Data
    name = fields.Char(string="Unit:")
    type = fields.Selection([
        ('one', 'One Person'),
        ('one_half', 'One And Half Person'),
        ('two', 'Two Person'),
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
                    ('name', 'ilike', "Mattress - "+(dict(record._fields['type'].selection).get(record.type))),
                    # ('level_of_dirt', '=', record.level_of_dirt.id)
                ], limit=1)
                record.product_id = product_id.id

    def get_time_of_cleaning(self):
        for record in self:
            record.time_in_mins = (record.qty * record.product_id.product_uom_qty)

    def get_selling_price(self):
        for record in self:
            record.s_price = (record.qty * record.price)