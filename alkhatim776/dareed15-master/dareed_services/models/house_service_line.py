from odoo import api, fields, models, _
import time
import math


class HouseKeepingLine(models.Model):
    _name = "house.keeping.line"

    # Main Data
    product_id = fields.Many2one('product.product', string="Product", domain="[('is_housekeeping', '=', True)]",
                                 required=True)
    type_of_service = fields.Many2one('house.keeping.type.of.service', string="Type")
    unit_of_measure = fields.Many2one('uom.uom', related="product_id.uom_id", string="UoM")
    unit_of_measure_qty = fields.Float(string='UoM Qty', related="product_id.product_uom_qty")
    qty = fields.Float("Item Qty")
    number_of_units = fields.Float("No. of units")
    total_qty = fields.Integer("Total Qty", compute="get_total_qty",store=True)
    frequency = fields.Integer("Frequency",  default=1)
    number_of_workers = fields.Float("Workers", default=1, digits=(12, 2))
    unit_price = fields.Float("Unit Price")
    total_price = fields.Float("Total Price", digits=(12, 2))
    calculate_round = fields.Float("Rounded", digits=(12, 2))
    service_id = fields.Many2one("house.service")
    markup = fields.Float("Mark-up", digits=(12, 4))

    @api.depends('product_id', 'qty', 'number_of_units', 'frequency', 'calculate_round')
    def get_total_qty(self):
        for record in self:
            record.total_qty = record.qty * record.number_of_units
            record.number_of_workers = (record.total_qty * record.frequency * record.unit_of_measure_qty) / (8 * 60)

    @api.onchange('product_id')
    def set_unit_price(self):
        for record in self:
            record.unit_price = record.product_id.list_price

