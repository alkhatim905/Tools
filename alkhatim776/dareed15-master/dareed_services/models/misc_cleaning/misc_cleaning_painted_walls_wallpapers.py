from odoo import api, fields, models, _


class MiscCleaningPaintedWallsWallpapers(models.Model):
    _name = "misc.cleaning.painted.walls.wallpapers"

    def get_product_id(self):
        return self.env['product.product'].search([
            ('name', '=', "Painted Walls & Wall paper"),
        ], limit=1).id

    # Main Data
    name = fields.Char(string="Painted Walls & Wall paper:")
    area_to_clean = fields.Float(string="Area To Clean")
    time_in_hours = fields.Float(string="Time (hours)", compute='get_time_of_cleaning')

    product_id = fields.Many2one("product.product", string="Product", default=get_product_id)
    service_id = fields.Many2one("house.service")

    def get_time_of_cleaning(self):
        for record in self:
            record.time_in_hours = (record.area_to_clean * record.product_id.product_uom_qty) / 60
