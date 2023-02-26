from odoo import api, fields, models, _
import time


class MarbleCleaningSurface(models.Model):
    _name = "marble.cleaning.surface"

    # Main Data
    name = fields.Char(string="Surface:")
    surface_type = fields.Selection([
        ('floor', 'Floor'),
        ('stairs', 'Stairs'),
        ('wall', 'Wall'),
    ], string="Surface Type", required=True)
    service_type = fields.Selection([
        ('treatment', 'Treatment'),
        ('polishing', 'Polishing')
    ], string="Service Type", required=True)

    area = fields.Float(string="Area")
    price = fields.Float(string="Unit price in SR", related='product_id.list_price')
    s_price = fields.Float(string="Selling price in SR", compute='get_selling_price')

    product_id = fields.Many2one("product.product", string="Product")
    service_id = fields.Many2one("house.service")
    time_in_hours = fields.Float(string="Time (Hours)", compute='get_time_in_hours')

    @api.onchange('surface_type', 'service_type')
    def get_product_id(self):
        for record in self:
            if record.service_type and record.surface_type:
                product_id = self.env['product.product'].search([
                    ('name', 'ilike',
                     "Marble " + (dict(record._fields['surface_type'].selection).get(record.surface_type)) +
                     " - " + (dict(record._fields['service_type'].selection).get(record.service_type))),
                ], limit=1)
                record.product_id = product_id.id

    def get_selling_price(self):
        for record in self:
            record.s_price = (record.area * record.price)

    def get_time_in_hours(self):
        for record in self:
            record.time_in_hours = (record.area * record.product_id.product_uom_qty) / 60
