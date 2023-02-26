from odoo import api, fields, models, _


class CleaningOrderLineByPiece(models.Model):
    _name = "cleaning.order.line.items.by.piece"
    # Main Data

    level_of_dirt = fields.Many2one('cleaning.level.of.dirtiness', string="Level of Dirtiness",
                                    related='service_id.cleaning_level_of_dirtiness', store=True)
    name = fields.Many2one('product.product', string="Items by Peace:", required=True)
    quantity = fields.Float(string="Quantity")
    time_in_hours = fields.Float(string="Time (hours)", compute='get_time_of_cleaning',store=True)

    @api.onchange('level_of_dirt')
    def reset_products_list(self):
        return {'domain': {'name': [('is_cleaning', '=', True), ('level_of_dirt', '=', self.level_of_dirt.id)]}}

    service_id = fields.Many2one("house.service")


    def get_time_of_cleaning(self):
        for record in self:
            record.time_in_hours = (record.quantity * record.name.product_uom_qty) / 60
