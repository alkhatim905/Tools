from odoo import api, fields, models, _


class MiscCleaningServiceItems(models.Model):
    _name = "misc.cleaning.service.items"

    def get_product_id(self):
        return self.env['product.product'].search([('name', '=', 'Service Items From Dareed')], limit=1).id

    # Main Data
    name = fields.Char(string="Service items from Dareed:")
    description = fields.Char(string="Description")
    time_in_hours = fields.Float(string="Time (hours)", default=1)

    product_id = fields.Many2one("product.product", string="Product", default=get_product_id)
    service_id = fields.Many2one("house.service")

