from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = "sale.order"

    house_service_id = fields.Many2one('house.service', "Service")

    service_type = fields.Selection([
        ('one_time', 'One Time'), ('contract', 'Contract')
    ], string="Service Type", default="one_time", required=True)
    number_of_workers = fields.Integer("Workers", default=1)
    time_from = fields.Selection([
        ('0', '12 AM'), ('1', '01 AM'), ('2', '02 AM'), ('3', '03 AM'), ('4', '04 AM'), ('5', '05 AM'), ('6', '06 AM'),
        ('7', '07 AM'), ('8', '08 AM'), ('9', '09 AM'), ('10', '10 AM'), ('11', '11 AM'), ('12', '12 PM'),
        ('13', '01 PM'), ('14', '02 PM'), ('15', '03 PM'), ('16', '04 PM'), ('17', '05 PM'), ('18', '06 PM'),
        ('19', '07 PM'), ('20', '08 PM'), ('21', '09 PM'), ('22', '10 PM'), ('23', '11 PM')
    ], string="From", default='10')
    time_to = fields.Selection([
        ('0', '12 AM'), ('1', '01 AM'), ('2', '02 AM'), ('3', '03 AM'), ('4', '04 AM'), ('5', '05 AM'), ('6', '06 AM'),
        ('7', '07 AM'), ('8', '08 AM'), ('9', '09 AM'), ('10', '10 AM'), ('11', '11 AM'), ('12', '12 PM'),
        ('13', '01 PM'), ('14', '02 PM'), ('15', '03 PM'), ('16', '04 PM'), ('17', '05 PM'), ('18', '06 PM'),
        ('19', '07 PM'), ('20', '08 PM'), ('21', '09 PM'), ('22', '10 PM'), ('23', '11 PM')
    ], string="To", default='18')

    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")

    start_day = fields.Selection([
        ('saturday', 'Saturday'), ('sunday', 'Sunday'), ('monday', 'Monday'), ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'), ('thursday', 'Thursday'), ('friday', 'Friday'),
    ], string="Start Day")
    end_day = fields.Selection([
        ('saturday', 'Saturday'), ('sunday', 'Sunday'), ('monday', 'Monday'), ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'), ('thursday', 'Thursday'), ('friday', 'Friday'),
    ], string="End Day")

    is_cleaning_service = fields.Boolean(string="Cleaning", related="house_service_id.is_cleaning_service")
    is_steam_service = fields.Boolean(string="Steam", related="house_service_id.is_steam_service")
    is_marble_service = fields.Boolean(string="Marble", related="house_service_id.is_marble_service")
    total_duration_hours = fields.Float(string="Total Hours", related="house_service_id.hours_of_project_with_risk")
    contracts = fields.Boolean(string="Contracts", related="house_service_id.contracts")
    customer_contact_person = fields.Many2one('res.partner', string="Customer Contact Person",
                                              related="house_service_id.customer_contact_person")

    total_duration_days = fields.Float(string="Estimated Working Days", related="house_service_id.total_duration_days")
    selected_quotation_areas = fields.Many2many('quotation.area', string="Internal Areas",
                                                related="house_service_id.selected_quotation_areas")
    selected_quotation_areas_external = fields.Many2many('quotation.area', string="External Areas",
                                                         related="house_service_id.selected_quotation_areas_external")

    selected_quotation_housekeeping_material = fields.Many2many('quotation.housekeeping.material',
                                                                string="Housekeeping Material",
                                                                related="house_service_id.selected_quotation_housekeeping_material")
    selected_quotation_cleaning_items = fields.Many2many('quotation.cleaning.item', string="Cleaning Items",
                                                         related="house_service_id.selected_quotation_cleaning_items")
    selected_quotation_cleaning_items_external = fields.Many2many('quotation.cleaning.item',
                                                                  string="External Cleaning Items", copy=True,
                                                                  domain=[('type', '=', 'external')],
                                                                  related="house_service_id.selected_quotation_cleaning_items_external")

    selected_quotation_cleaning_material = fields.Many2many('quotation.cleaning.material', string="Cleaning Material",
                                                            copy=True,
                                                            related="house_service_id.selected_quotation_cleaning_material")

    indoor_cleanings_all = fields.One2many('cleaning.order.line.all', string="Indoor Cleaning All",
                                           related="house_service_id.indoor_cleanings_all")
    indoor_outside_yard_floor = fields.One2many('cleaning.order.line.outside.yard.floor', string="Outside Yard Floor",
                                                related="house_service_id.indoor_outside_yard_floor")

    selected_quotation_steam_items = fields.Many2many('quotation.steam.item', string="Steam Items",
                                                      related="house_service_id.selected_quotation_steam_items")
    selected_quotation_steam_material = fields.Many2many('quotation.steam.material', string="Steam Material", copy=True,
                                                         related="house_service_id.selected_quotation_steam_material")
    selected_quotation_marble_items = fields.Many2many('quotation.marble.item', string="Marble Items",
                                                       related="house_service_id.selected_quotation_marble_items")
    selected_quotation_marble_material = fields.Many2many('quotation.marble.material', string="Marble Material",
                                                          related="house_service_id.selected_quotation_marble_material")

    selected_quotation_equipments = fields.Many2many('quotation.equipment', string="Equipments",
                                                     related="house_service_id.selected_quotation_equipments")
    selected_quotation_spare_parts = fields.Many2many('quotation.spare.part', string="Spare Parts",
                                                      related="house_service_id.selected_quotation_spare_parts")
    selected_quotation_tools = fields.Many2many('quotation.tool', string="Tools",
                                                related="house_service_id.selected_quotation_tools")
    user_id = fields.Many2one('res.users', string='Salesperson', tracking=True,
                              track_sequence=2, default=lambda self: self.env.user,
                              related="house_service_id.salesperson")
    total_cleaning_price = fields.Float('Total Cleaning Price', digits=dp.get_precision('Product Price'),
                                        compute='_compute_cleaning_totals')
    total_cleaning_quantity = fields.Float('Total Cleaning Quantity',
                                           digits=dp.get_precision('Product Unit of Measure'),
                                           compute='_compute_cleaning_totals')
    total_cleaning_subtotal = fields.Monetary('Cleaning Subtotal', compute='_compute_cleaning_totals')

    @api.depends('order_line', 'order_line.product_id', 'order_line.product_uom_qty', 'order_line.price_unit',
                 'order_line.price_subtotal')
    def _compute_cleaning_totals(self):
        for rec in self:
            total_cleaning_price = 0.0
            total_cleaning_quantity = 0.0
            total_cleaning_subtotal = 0.0
            for line in rec.order_line:
                if line.product_id and (line.product_id.is_cleaning or line.product_id.is_cleaning_misc):
                    total_cleaning_price += line.price_unit
                    total_cleaning_quantity += line.product_uom_qty
                    total_cleaning_subtotal += line.price_subtotal
            rec.total_cleaning_price = total_cleaning_price
            rec.total_cleaning_quantity = total_cleaning_quantity
            rec.total_cleaning_subtotal = total_cleaning_subtotal
