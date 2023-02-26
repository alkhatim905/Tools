from odoo import api, fields, models, _


class SteamCleaningCurtains(models.Model):
    _name = "steam.cleaning.curtains"

    # Main Data
    name = fields.Char(string="Unit:")
    type = fields.Selection([
        ('light', 'Light'),
        ('heavy', 'Heavy'),
        ('chiffon', 'Chiffon')
    ], required=True)
    is_chiffon = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], required=True)
    qty = fields.Float(string="Qty of Unit")
    price = fields.Float(string="Unit price in SR", compute='get_product_id')
    s_price = fields.Float(string="Selling price in SR", compute='get_selling_price')
    time_in_mins = fields.Float(string="Time (Minutes)", compute='get_time_of_cleaning')

    product_id = fields.Many2one("product.product", string="Product")
    service_id = fields.Many2one("house.service")

    @api.onchange('type', 'is_chiffon')
    def get_product_id(self):
        for record in self:
            if record.is_chiffon and record.type:
                product_id = self.env['product.product'].search([
                    ('name', 'ilike', "Curtain - "+(dict(record._fields['type'].selection).get(record.type))),
                ], limit=1)
                record.product_id = product_id.id
                record.price = product_id.list_price
                if record.is_chiffon == 'yes':
                    chiffon_id = self.env['product.product'].search([
                        ('name', 'ilike', "Curtain - Chiffon"),
                    ], limit=1)
                    record.price += chiffon_id.list_price

    def get_time_of_cleaning(self):
        for record in self:
            record.time_in_mins = (record.qty * record.product_id.product_uom_qty)
            if record.is_chiffon == 'yes':
                product_id = self.env['product.product'].search([
                    ('name', 'ilike', "Curtain - Chiffon"),
                ], limit=1)
                record.time_in_mins += record.qty * product_id.product_uom_qty

    
    def get_selling_price(self):
        for record in self:
            record.s_price = (record.qty * record.price)
