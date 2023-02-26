from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CleaningOrderLineAll(models.Model):
    _name = "cleaning.order.line.all"

    # Main Data
    name = fields.Char(string="Indoor cleaning (All):")
    floor_area = fields.Float(string="% Floor Area")
    with_furniture = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="With Furniture?", required=True)
    area_to_clean = fields.Float(string="Area To Clean", compute='get_area_to_clean',store=True)
    time_in_hours = fields.Float(string="Time (hours)", compute='get_time_of_cleaning',store=True)

    product_id = fields.Many2one("product.product", string="Product", compute="get_product_id",store=True)
    service_id = fields.Many2one("house.service")
    level_of_dirt = fields.Many2one('cleaning.level.of.dirtiness', related='service_id.cleaning_level_of_dirtiness',
                                    string="Level of Dirtiness")
    customer_type = fields.Many2one('cleaning.customer.type', related='service_id.cleaning_customer_type')

    @api.depends('level_of_dirt', 'customer_type')
    def get_product_id(self):
        customer_type = ''
        if len(self):
            customer_type = "Indoor Cleaning Villa" if self[0].customer_type.name == 'Villa' else "Indoor Cleaning Other"
        for record in self:
            if not record.level_of_dirt and record.area_to_clean > 0:
                raise ValidationError(_("You can't add cleaning lines without choosing level of dirtiness."))
            if not record.customer_type and record.area_to_clean > 0:
                raise ValidationError(_("You can't add cleaning lines without choosing specific customer type."))
            product_id = self.env['product.product'].search([
                ('name', 'ilike', customer_type),
                ('level_of_dirt', '=', record.level_of_dirt.id)
            ], limit=1)
            record.product_id = product_id.id

    def get_area_to_clean(self):
        for record in self:
            if record.customer_type and record.level_of_dirt:
                record.area_to_clean = (record.floor_area / 100) * record.service_id.cleaning_one_floor_area

    def get_time_of_cleaning(self):
        for record in self:
            record.time_in_hours = (record.area_to_clean * record.product_id.product_uom_qty) / 60
            if record.with_furniture == 'yes':
                record.time_in_hours = record.time_in_hours * 1.15
            elif record.with_furniture != 'no':
                record.time_in_hours = 0
