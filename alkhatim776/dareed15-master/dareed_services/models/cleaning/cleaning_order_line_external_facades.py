from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CleaningOrderLineExternalFacades(models.Model):
    _name = "cleaning.order.line.external.facades"

    # Main Data
    name = fields.Char(string="Items by Area:")
    area_to_clean = fields.Float(string="Area")
    time_in_hours = fields.Float(string="Time (hours)", compute='get_time_of_cleaning',store=True)

    product_id = fields.Many2one("product.product", string="Product", compute="get_product_id",store=True)
    service_id = fields.Many2one("house.service")
    level_of_dirt = fields.Many2one('cleaning.level.of.dirtiness', string="Level of Dirtiness",
                                    related='service_id.cleaning_level_of_dirtiness')

    @api.depends('level_of_dirt')
    def get_product_id(self):
        for record in self:
            if record.area_to_clean > 0:
                if not record.level_of_dirt:
                    raise ValidationError(_("Please select level of dirtiness"))
            product_id = self.env['product.product'].search([
                ('name', 'ilike', "External Facades - " + record.name),
                ('level_of_dirt', '=', record.level_of_dirt.id)
            ], limit=1)
            record.product_id = product_id.id

    def get_time_of_cleaning(self):
        for record in self:
            record.time_in_hours = (record.area_to_clean * record.product_id.product_uom_qty) / 60
