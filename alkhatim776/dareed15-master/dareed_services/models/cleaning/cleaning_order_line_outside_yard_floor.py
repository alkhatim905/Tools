from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CleaningOrderLineOutsideYardFloor(models.Model):
    _name = "cleaning.order.line.outside.yard.floor"

    # Main Data
    name = fields.Char(string="outside yard floor:")
    length = fields.Float(string="Length")
    width = fields.Float(string="Width")
    area_to_clean = fields.Float(string="Area To Clean", compute='get_area_to_clean',store=True)
    time_in_hours = fields.Float(string="Time (hours)", compute='get_time_of_cleaning',store=True)

    product_id = fields.Many2one("product.product", string="Product", compute="get_product_id")
    service_id = fields.Many2one("house.service")
    level_of_dirt = fields.Many2one('cleaning.level.of.dirtiness', related='service_id.cleaning_level_of_dirtiness',
                                    string="Level of Dirtiness")

    @api.depends('level_of_dirt')
    def get_product_id(self):
        for record in self:
            if record.area_to_clean > 0:
                if not record.level_of_dirt:
                    raise ValidationError(_("Please select level of dirtiness"))

            product_id = self.env['product.product'].search([
                ('name', 'ilike', "Outside yard floor - "+record.name),
                ('level_of_dirt', '=', record.level_of_dirt.id)
            ], limit=1)
            record.product_id = product_id.id

    def get_area_to_clean(self):
        for record in self:
            if record.level_of_dirt:
                record.area_to_clean = record.length * record.width
            else:
                return False

    def get_time_of_cleaning(self):
        for record in self:
            record.time_in_hours = (record.area_to_clean * record.product_id.product_uom_qty) / 60
