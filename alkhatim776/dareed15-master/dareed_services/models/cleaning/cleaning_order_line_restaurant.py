from odoo import api, fields, models, _


class CleaningOrderLineRestaurant(models.Model):
    _name = "cleaning.order.line.restaurant"

    # Main Data
    name = fields.Char(string="Indoor cleaning (Restaurant):")
    area_to_clean = fields.Float(string="Area To Clean")
    level_of_dirtiness = fields.Many2one("cleaning.level.of.dirtiness", default=1)
    time_in_hours = fields.Float(string="Time (hours)", compute='get_time_of_cleaning',store=True)

    product_id = fields.Many2one("product.product", string="Product", compute="get_product_id",store=True)
    service_id = fields.Many2one("house.service")

    def get_product_id(self):
        for record in self:
            product_id = self.env['product.product'].search([
                ('name', 'ilike', "Indoor Cleaning Other"),
                ('level_of_dirt', '=', record.level_of_dirtiness.id)
            ], limit=1)
            record.product_id = product_id.id

    def get_time_of_cleaning(self):
        for record in self:
            record.time_in_hours = (record.area_to_clean * record.product_id.product_uom_qty) / 60
            if 'Kitchen' in record.name:
                record.time_in_hours = record.time_in_hours * 1.10
