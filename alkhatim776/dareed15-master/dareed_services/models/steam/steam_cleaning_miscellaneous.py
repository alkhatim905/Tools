from odoo import api, fields, models, _


class SteamCleaningMiscellaneous(models.Model):
    _name = "steam.cleaning.miscellaneous"

    # Main Data
    name = fields.Many2one('product.product', string="Service Item:", domain="[('is_steam', '=', True)]",
                           required=True)
    unit = fields.Many2one('uom.uom', related='name.uom_id')
    qty = fields.Float(string="Qty of Unit")
    price = fields.Float(string="Unit price in SR", related='name.list_price')
    s_price = fields.Float(string="Selling price in SR", compute='get_selling_price')
    time_in_mins = fields.Float(string="Time (Minutes)", compute='get_time_of_cleaning')

    service_id = fields.Many2one("house.service")

    def get_time_of_cleaning(self):
        for record in self:
            record.time_in_mins = (record.qty * record.name.product_uom_qty)

    def get_selling_price(self):
        for record in self:
            record.s_price = (record.qty * record.price)
