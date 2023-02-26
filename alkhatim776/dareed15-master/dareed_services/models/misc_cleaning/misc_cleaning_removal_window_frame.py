from odoo import api, fields, models, _


class MiscCleaningRemovalWindowFrame(models.Model):
    _name = "misc.cleaning.removal.window.frame"

    # Main Data
    name = fields.Char(string="Removal of Window frame sticker:")
    state = fields.Selection([
        ('new', 'New'),
        ('old', 'Old')
    ], string="State", required=True)
    linear_m = fields.Float(string="Linear M")
    time_in_hours = fields.Float(string="Time (hours)", compute='get_time_of_cleaning')

    product_id = fields.Many2one("product.product", string="Product")
    service_id = fields.Many2one("house.service")

    @api.onchange('state')
    def get_product_id(self):
        for record in self:
            if record.state:
                product_id = self.env['product.product'].search([
                    ('name', '=', "Removal of Window frame sticker - " + ('New' if record.state == 'new' else 'Old'))
                ], limit=1)
                record.product_id = product_id.id

    def get_time_of_cleaning(self):
        for record in self:
            if record.product_id:
                record.time_in_hours = (record.linear_m * record.product_id.product_uom_qty) / 60
