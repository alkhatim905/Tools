from odoo import api, fields, models, _


class MiscCleaningWindows(models.Model):
    _name = "misc.cleaning.windows"

    # Main Data
    name = fields.Char(string="Windows:")
    level_of_dirtiness = fields.Many2one("cleaning.level.of.dirtiness", string="Level Of Dirtiness", required=True)
    length = fields.Float(string="Length")
    width = fields.Float(string="Width")
    qty = fields.Integer(string="Qty")
    area_to_clean = fields.Float(string="Area To Clean", compute='get_area_to_clean')
    time_in_hours = fields.Float(string="Time (hours)", compute='get_time_of_cleaning')

    product_id = fields.Many2one("product.product", string="Product")
    service_id = fields.Many2one("house.service")

    def get_area_to_clean(self):
        for record in self:
            record.area_to_clean = record.length * record.width * record.qty

    @api.onchange('level_of_dirtiness')
    def get_product_id(self):
        for record in self:
            if record.level_of_dirtiness:
                product_id = self.env['product.product'].search([
                    ('name', '=', "Windows"),
                    ('level_of_dirt', '=', record.level_of_dirtiness.id)
                ], limit=1)
                record.product_id = product_id.id

    
    def get_time_of_cleaning(self):
        for record in self:
            if record.product_id:
                record.time_in_hours = (record.area_to_clean * record.product_id.product_uom_qty) / 60
