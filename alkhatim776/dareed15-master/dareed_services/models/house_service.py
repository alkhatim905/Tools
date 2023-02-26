from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import math


class HouseService(models.Model):
    _name = "house.service"
    _inherit = ["mail.thread"]

    # Main Data
    name = fields.Char(string="Name")
    date = fields.Date("Date")
    customer = fields.Many2one("res.partner", string="Customer", required=True, copy=True)
    sale_order_id = fields.Many2one('sale.order', string="Sale Order Related", tracking=True, copy=False)
    project_id = fields.Many2one('project.project', string="Project Cleaning & Steam", tracking=True, copy=False)
    project_marble_id = fields.Many2one('project.project', string="Project Marble", tracking=True, copy=False)
    salesperson = fields.Many2one("res.users", string="Sales Rep.")
    customer_contact_person = fields.Many2one('res.partner', string="Customer Contact Person")
    customer_contact_number = fields.Char(string="Customer Contact Phone", related="customer_contact_person.phone")
    hours_of_cleaning_quick = fields.Float(string="Hours Of Cleaning (Quick)", compute="compute_proposal_details")
    hours_of_cleaning_misc = fields.Float(string="Hours Of Cleaning (Misc.)", compute="compute_proposal_details")
    hours_of_cleaning_risk_hours = fields.Float(string="Project Extra Risk Hours (Cleaning)")
    hours_of_cleaning_total = fields.Float(string="Total Cleaning Hours", compute="re_calculate_total_hours")
    hours_of_marble = fields.Float(string="Hours Of Cleaning", compute="compute_proposal_details")
    hours_of_marble_risk_hours = fields.Float(string="Project Extra Risk Hours (Marble)")
    hours_of_marble_total = fields.Float(string="Total Marble Hours", compute="re_calculate_total_hours")
    hours_of_steam = fields.Float(string="Hours Of Cleaning", compute="compute_proposal_details")
    hours_of_steam_risk_hours = fields.Float(string="Project Extra Risk Hours (Steam)")
    hours_of_steam_total = fields.Float(string="Total Steam Hours", compute="re_calculate_total_hours")
    hours_of_project_with_risk = fields.Float(string="Total Hours (With Risks)", compute="re_calculate_total_hours")
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', help="Pricelist for current Sheet.")
    active = fields.Boolean(string="Active", default=True)

    def toggle_archived(self):
        for record in self:
            record.active = not record.active

    @api.onchange('hours_of_cleaning_risk_hours', 'hours_of_steam_risk_hours', 'hours_of_marble_risk_hours')
    def re_calculate_total_hours(self):
        for record in self:
            record.hours_of_cleaning_total = record.hours_of_cleaning_risk_hours + record.hours_of_cleaning_quick \
                                             + record.hours_of_cleaning_misc
            record.hours_of_steam_total = record.hours_of_steam_risk_hours + record.hours_of_steam
            record.hours_of_marble_total = record.hours_of_marble_risk_hours + record.hours_of_marble
            record.hours_of_project_with_risk = record.hours_of_cleaning_total + record.hours_of_marble_total \
                                                + record.hours_of_steam_total
            record.total_duration_hours = record.hours_of_project_with_risk
            record.total_planned_workers = record.hours_of_project_with_risk / 8

    # House Keeping Data
    house_keeping = fields.One2many("house.keeping.line", "service_id", string="House Keeping", copy=True)

    # Cleaning Data
    cleaning_customer_type = fields.Many2one("cleaning.customer.type", string="Customer Type", copy=True)
    cleaning_level_of_dirtiness = fields.Many2one("cleaning.level.of.dirtiness", string="Level Of Dirtiness", copy=True)
    cleaning_length_of_one_floor = fields.Float("Length Of One Floor", copy=True)
    cleaning_width_of_one_floor = fields.Float("Width Of One Floor", copy=True)
    cleaning_one_floor_area = fields.Float("Area Of One Floor", compute='get_cleaning_floor_area', copy=True)

    state = fields.Selection([
        ('new', 'New'),
        ('quoted', 'Quoted')
    ], default='new', copy=True)
    calculate_markup = fields.Float("Calculate-markup", compute="get_markup",store=True)

    def get_markup(self):
        for record in self:
            sum = 0.0
            for line in record.house_keeping:
                sum += line.number_of_workers
            sum_rounded = float(math.ceil(sum))
            if sum != 0:
                house_keeping_markup = float(sum_rounded / sum)
            else:
                house_keeping_markup = 1
            for line in record.house_keeping:
                line.write({"markup": house_keeping_markup})
                line.write({"calculate_round": house_keeping_markup * line.number_of_workers})
                line.write({"total_price": house_keeping_markup * line.number_of_workers *
                                           self.env['ir.default'].get("res.config.settings", "worker_rate")})

    @api.depends('cleaning_length_of_one_floor', 'cleaning_width_of_one_floor', )
    def get_cleaning_floor_area(self):
        for record in self:
            record.cleaning_one_floor_area = record.cleaning_length_of_one_floor * record.cleaning_width_of_one_floor

    @api.constrains('indoor_cleanings_all', 'indoor_items_by_width_and_length', 'indoor_outside_yard_floor',
                    'indoor_items_by_area', 'indoor_external_facades', 'indoor_items_by_piece')
    def auto_compute_area(self):
        self.ensure_one()
        for line in self.indoor_cleanings_all:
            matching_area = self.env['quotation.area'].search(
                [('name_en', 'ilike', line.name), ('type', '=', 'internal')], limit=1)
            if matching_area:
                if line.floor_area > 0:
                    self.write({'selected_quotation_areas': [(4, matching_area.id)]})
                else:
                    self.write({'selected_quotation_areas': [(3, matching_area.id)]})
        for line in self.indoor_items_by_width_and_length:
            matching_area = self.env['quotation.area'].search(
                [('name_en', 'ilike', line.name), ('type', '=', 'external')], limit=1)
            if matching_area:
                if line.area_to_clean > 0:
                    self.write({'selected_quotation_areas_external': [(4, matching_area.id)]})
                else:
                    self.write({'selected_quotation_areas_external': [(3, matching_area.id)]})
        indoor_outside_yard_floor_flag = False
        for line in self.indoor_outside_yard_floor:
            matching_area = self.env['quotation.area'].search(
                [('name_en', 'ilike', line.name), ('type', '=', 'external')], limit=1)
            if matching_area:
                if line.area_to_clean > 0:
                    self.write({'selected_quotation_areas_external': [(4, matching_area.id)]})
                    flag = True
                else:
                    self.write({'selected_quotation_areas_external': [(3, matching_area.id)]})
        if indoor_outside_yard_floor_flag:
            matching_area = self.env['quotation.area'].search(
                [('name_en', 'ilike', 'Outside Yard Floor'), ('type', '=', 'external')], limit=1)
            self.write({'selected_quotation_areas_external': [(3, matching_area.id)]})
            if matching_area:
                self.write({'selected_quotation_areas_external': [(4, matching_area.id)]})
        else:
            matching_area = self.env['quotation.area'].search(
                [('name_en', 'ilike', 'Outside Yard Floor'), ('type', '=', 'external')], limit=1)
            if matching_area:
                self.write({'selected_quotation_areas_external': [(3, matching_area.id)]})

        for line in self.indoor_items_by_area:
            matching_area = self.env['quotation.area'].search(
                [('name_en', 'ilike', line.name), ('type', '=', 'external')], limit=1)
            if matching_area:
                if line.area_to_clean > 0:
                    self.write({'selected_quotation_areas_external': [(4, matching_area.id)]})
                else:
                    self.write({'selected_quotation_areas_external': [(3, matching_area.id)]})
        for line in self.indoor_items_by_piece:
            matching_area = self.env['quotation.area'].search(
                [('name_en', 'ilike', line.name.name), ('type', '=', 'external')], limit=1)
            if matching_area:
                if line.quantity > 0:
                    self.write({'selected_quotation_areas_external': [(4, matching_area.id)]})
                else:
                    self.write({'selected_quotation_areas_external': [(3, matching_area.id)]})

    @api.constrains('indoor_outside_yard_floor', 'indoor_curtains', 'indoor_items_by_area', 'indoor_items_by_piece',
                    'indoor_external_facades', 'indoor_items_by_width_and_length')
    def auto_compute_items(self):
        self.ensure_one()
        indoor_outside_yard_floor_flag = False
        for line in self.indoor_outside_yard_floor:
            if line.name == 'Drop ceiling':
                line.name = 'Drop Ceiling'
            matching_item = self.env['quotation.cleaning.item'].search(
                [('name_en', 'ilike', line.name), ('type', '=', 'internal')], limit=1)
            if matching_item:
                if line.area_to_clean > 0:
                    indoor_outside_yard_floor_flag = True
                    self.write({'selected_quotation_cleaning_items': [(4, matching_item.id)]})
                else:
                    self.write({'selected_quotation_cleaning_items': [(3, matching_item.id)]})
            matching_item = self.env['quotation.cleaning.item'].search(
                [('name_en', 'ilike', line.name), ('type', '=', 'external')], limit=1)
            if matching_item:
                if line.area_to_clean > 0:
                    indoor_outside_yard_floor_flag = True
                    self.write({'selected_quotation_cleaning_items_external': [(4, matching_item.id)]})
                else:
                    self.write({'selected_quotation_cleaning_items_external': [(3, matching_item.id)]})

        if indoor_outside_yard_floor_flag:
            matching_item = self.env['quotation.cleaning.item'].search(
                [('name_en', 'ilike', 'Outside Yard Floor'), ('type', '=', 'external')], limit=1)
            if matching_item:
                self.write({'selected_quotation_cleaning_items_external': [(4, matching_item.id)]})
        else:
            matching_item = self.env['quotation.cleaning.item'].search(
                [('name_en', 'ilike', 'Outside Yard Floor'), ('type', '=', 'external')], limit=1)
            if matching_item:
                self.write({'selected_quotation_cleaning_items_external': [(3, matching_item.id)]})

        matching_item = self.env['quotation.cleaning.item'].search(
            [('name_en', 'ilike', "Curtains (vacuum)"), ('type', '=', 'internal')], limit=1)
        if len(self.indoor_curtains):
            self.write({'selected_quotation_cleaning_items': [(4, matching_item.id)]})
        else:
            self.write({'selected_quotation_cleaning_items': [(3, matching_item.id)]})

        for line in self.indoor_items_by_area:
            matching_item = self.env['quotation.cleaning.item'].search(
                [('name_en', 'ilike', line.name), ('type', '=', 'internal')], limit=1)
            if matching_item:
                if line.area_to_clean > 0:
                    self.write({'selected_quotation_cleaning_items': [(4, matching_item.id)]})
                else:
                    self.write({'selected_quotation_cleaning_items': [(3, matching_item.id)]})

            if line.name == 'Fence':
                matching_item = self.env['quotation.cleaning.item'].search(
                    [('name_en', '=ilike', line.name), ('type', '=', 'external')])
                for matching_line in matching_item:
                    if line.area_to_clean > 0.0:
                        self.write({'selected_quotation_cleaning_items_external': [(4, matching_line.id)]})
                    else:
                        self.write({'selected_quotation_cleaning_items_external': [(3, matching_line.id)]})
            else:
                matching_item = self.env['quotation.cleaning.item'].search(
                    [('name_en', 'ilike', line.name), ('type', '=', 'external')], limit=1)
                if matching_item:
                    if line.area_to_clean > 0:
                        self.write({'selected_quotation_cleaning_items_external': [(4, matching_item.id)]})
                    else:
                        self.write({'selected_quotation_cleaning_items_external': [(3, matching_item.id)]})

        for line in self.indoor_items_by_piece:
            if line.name and line.name.name.startswith('Chandeliers'):
                matching_item = self.env['quotation.cleaning.item'].search(
                    [('name_en', '=ilike', 'Chandeliers'), ('type', '=', 'internal')], limit=1)
                if matching_item:
                    if line.quantity > 0.0:
                        self.write({'selected_quotation_cleaning_items': [(3, matching_item.id)]})
                    else:
                        self.write({'selected_quotation_cleaning_items': [(4, matching_item.id)]})
            else:
                if line.name:
                    matching_item = self.env['quotation.cleaning.item'].search(
                        [('name_en', '=ilike', line.name.name), ('type', '=', 'internal')], limit=1)
                    if matching_item:
                        if line.quantity > 0.0:
                            self.write({'selected_quotation_cleaning_items': [(4, matching_item.id)]})
                        else:
                            self.write({'selected_quotation_cleaning_items': [(3, matching_item.id)]})
                    matching_item = self.env['quotation.cleaning.item'].search(
                        [('name_en', '=ilike', line.name.name), ('type', '=', 'external')], limit=1)
                    if matching_item:
                        if line.quantity > 0.0:
                            self.write({'selected_quotation_cleaning_items_external': [(4, matching_item.id)]})
                        else:
                            self.write({'selected_quotation_cleaning_items_external': [(3, matching_item.id)]})

        for line in self.indoor_items_by_width_and_length:
            matching_item = self.env['quotation.cleaning.item'].search(
                [('name_en', '=ilike', line.name), ('type', '=', 'internal')], limit=1)
            if matching_item:
                if line.area_to_clean > 0.0:
                    self.write({'selected_quotation_cleaning_items': [(4, matching_item.id)]})
                else:
                    self.write({'selected_quotation_cleaning_items': [(3, matching_item.id)]})
            matching_item = self.env['quotation.cleaning.item'].search(
                [('name_en', '=ilike', line.name), ('type', '=', 'external')], limit=1)
            if matching_item:
                if line.area_to_clean > 0.0:
                    self.write({'selected_quotation_cleaning_items_external': [(4, matching_item.id)]})
                else:
                    self.write({'selected_quotation_cleaning_items_external': [(3, matching_item.id)]})

        for line in self.indoor_external_facades:
            matching_item = self.env['quotation.cleaning.item'].search(
                [('name_en', '=ilike', line.name), ('type', '=', 'internal')], limit=1)
            if matching_item:
                if line.area_to_clean > 0.0:
                    self.write({'selected_quotation_cleaning_items': [(4, matching_item.id)]})
                else:
                    self.write({'selected_quotation_cleaning_items': [(3, matching_item.id)]})
            matching_item = self.env['quotation.cleaning.item'].search(
                [('name_en', '=ilike', line.name), ('type', '=', 'external')], limit=1)
            if matching_item:
                if line.area_to_clean > 0.0:
                    self.write({'selected_quotation_cleaning_items_external': [(4, matching_item.id)]})
                else:
                    self.write({'selected_quotation_cleaning_items_external': [(3, matching_item.id)]})

    def get_default_indoor_cleanings_all(self):
        return [
            [0, 0, {"name": "Basement", "with_furniture": "no"}],
            [0, 0, {"name": "Ground Floor", "with_furniture": "no"}],
            [0, 0, {"name": "First Floor", "with_furniture": "no"}],
            [0, 0, {"name": "Second Floor", "with_furniture": "no"}],
            [0, 0, {"name": "Roof Annex", "with_furniture": "no"}],
        ]

    def get_default_indoor_cleanings_restaurant(self):
        return [
            [0, 0, {"name": "Dinning Hall"}],
            [0, 0, {"name": "Kitchen"}],
        ]

    def get_default_indoor_items_by_width_and_length(self):
        return [
            [0, 0, {"name": "Brick Roof"}],
            [0, 0, {"name": "Normal Roof"}],
            [0, 0, {"name": "Car Shade"}],
            [0, 0, {"name": "Skylight"}],
            [0, 0, {"name": "Outside Annex"}],
            [0, 0, {"name": "Swimming Pool"}],
        ]

    def get_default_indoor_outside_yard_floor(self):
        return [
            [0, 0, {"name": "Terra-cotta"}],
            [0, 0, {"name": "Smooth tiles"}],
            [0, 0, {"name": "Rough tiles"}],
            [0, 0, {"name": "Marble cleaning"}],
        ]

    def get_default_indoor_items_by_area(self):
        return [
            [0, 0, {"name": "Drop Ceiling"}],
            [0, 0, {"name": "Fence"}]
        ]

    def get_default_indoor_external_facades(self):
        return [
            [0, 0, {"name": "Glass"}],
            [0, 0, {"name": "Mica or Marble"}],
            [0, 0, {"name": "Stone"}],
        ]

    indoor_cleanings_all = fields.One2many("cleaning.order.line.all", "service_id", string="All",
                                           default=get_default_indoor_cleanings_all, copy=True)
    indoor_cleanings_restaurant = fields.One2many("cleaning.order.line.restaurant", "service_id", string="Restaurants",
                                                  default=get_default_indoor_cleanings_restaurant, copy=True)
    indoor_items_by_width_and_length = fields.One2many("cleaning.order.line.width.length", "service_id",
                                                       string="By width and length",
                                                       default=get_default_indoor_items_by_width_and_length, copy=True)
    indoor_outside_yard_floor = fields.One2many("cleaning.order.line.outside.yard.floor", "service_id",
                                                string="Outside Yard Floor",
                                                default=get_default_indoor_outside_yard_floor, copy=True)
    indoor_curtains = fields.One2many("cleaning.order.line.curtains", "service_id", string="Curtains (vacuum)",
                                      copy=True)
    indoor_items_by_area = fields.One2many("cleaning.order.line.items.by.area", "service_id", string="Items by Area:",
                                           default=get_default_indoor_items_by_area, copy=True)
    indoor_external_facades = fields.One2many("cleaning.order.line.external.facades", "service_id",
                                              string="External Facades", default=get_default_indoor_external_facades,
                                              copy=True)
    indoor_items_by_piece = fields.One2many("cleaning.order.line.items.by.piece", "service_id",
                                            string="Items by Piece:", copy=True)

    # Misc. Cleaning Data
    misc_cleaning_porcelain_ceramic = fields.One2many("misc.cleaning.porcelain.ceramic", "service_id", copy=True)
    misc_cleaning_marble = fields.One2many("misc.cleaning.marble", "service_id", copy=True)
    misc_cleaning_parkay = fields.One2many("misc.cleaning.parkay", "service_id", copy=True)
    misc_cleaning_painted_walls_wallpapers = fields.One2many("misc.cleaning.painted.walls.wallpapers", "service_id",
                                                             copy=True)
    misc_cleaning_windows_shutter = fields.One2many("misc.cleaning.windows.shutter", "service_id", copy=True)
    misc_cleaning_windows = fields.One2many("misc.cleaning.windows", "service_id", copy=True)
    misc_cleaning_removal_window_frame = fields.One2many("misc.cleaning.removal.window.frame", "service_id", copy=True)
    misc_cleaning_service_items = fields.One2many("misc.cleaning.service.items", "service_id", copy=True)
    misc_cleaning_3rd_party_items = fields.One2many("misc.cleaning.3rd.party.item", "service_id", copy=True)
    misc_cleaning_miscellaneous_item = fields.One2many("misc.cleaning.miscellaneous", "service_id", copy=True)

    # Steam Data
    steam_cleaning_mocket = fields.One2many("steam.cleaning.mocket", "service_id", copy=True)
    steam_cleaning_carpets = fields.One2many("steam.cleaning.carpets", "service_id", copy=True)
    steam_cleaning_arabic_seat = fields.One2many("steam.cleaning.arabic.seat", "service_id", copy=True)
    steam_cleaning_mattress = fields.One2many("steam.cleaning.mattress", "service_id", copy=True)
    steam_cleaning_curtains = fields.One2many("steam.cleaning.curtains", "service_id", copy=True)
    steam_cleaning_miscellaneous = fields.One2many("steam.cleaning.miscellaneous", "service_id", copy=True)

    # Marble Data
    marble_cleaning_surface = fields.One2many("marble.cleaning.surface", "service_id", copy=True)
    marble_polishing_surface = fields.One2many("marble.polishing.surface", "service_id", copy=True)
    marble_protection_surface = fields.One2many("marble.protection.surface", "service_id", copy=True)
    marble_extra_items = fields.One2many("marble.extra.items", "service_id", copy=True)
    marble_miscellaneous_item = fields.One2many("marble.cleaning.miscellaneous", "service_id", copy=True)

    # Quotation Data
    is_cleaning_service = fields.Boolean(string="Cleaning", default=False, compute="compute_proposal_details")
    is_steam_service = fields.Boolean(string="Steam", default=False, compute="compute_proposal_details")
    is_marble_service = fields.Boolean(string="Marble", default=False, compute="compute_proposal_details")
    is_cleaning_service_saved = fields.Boolean(string="Cleaning Saved", default=False, save=True)
    is_steam_service_saved = fields.Boolean(string="Steam Saved", default=False, save=True)
    is_marble_service_saved = fields.Boolean(string="Marble Saved", default=False, save=True)
    total_duration_hours = fields.Float(string="Total Hours", realated="hours_of_project_with_risk")
    total_planned_workers = fields.Float(string="Total Workers", compute="re_calculate_total_hours")
    contracts = fields.Boolean(string="Contracts", default=False)

    total_duration_days = fields.Float(string="Estimated Working Days")
    selected_quotation_areas = fields.Many2many('quotation.area', relation='quotation_area_rel',
                                                string="Internal Areas", copy=True, domain=[('type', '=', 'internal')])
    selected_quotation_areas_external = fields.Many2many('quotation.area', relation='quotation_area_ext_rel',
                                                         string="External Areas", copy=True,
                                                         domain=[('type', '=', 'external')])
    selected_quotation_housekeeping_material = fields.Many2many('quotation.housekeeping.material',
                                                                string="Housekeeping Material", copy=True)
    selected_quotation_cleaning_items = fields.Many2many('quotation.cleaning.item', relation='quotation_clean_rel',
                                                         string="Internal Cleaning Items", copy=True,
                                                         domain=[('type', '=', 'internal')])
    selected_quotation_cleaning_items_external = fields.Many2many('quotation.cleaning.item',
                                                                  relation='quotation_clean_ext_rel',
                                                                  string="External Cleaning Items", copy=True,
                                                                  domain=[('type', '=', 'external')])
    selected_quotation_cleaning_material = fields.Many2many('quotation.cleaning.material', string="Cleaning Material",
                                                            copy=True)
    selected_quotation_steam_items = fields.Many2many('quotation.steam.item', string="Steam Items", copy=True)
    selected_quotation_steam_material = fields.Many2many('quotation.steam.material', string="Steam Material", copy=True)
    selected_quotation_marble_items = fields.Many2many('quotation.marble.item', string="Marble Items", copy=True)
    selected_quotation_marble_material = fields.Many2many('quotation.marble.material', string="Marble Material",
                                                          copy=True)

    selected_quotation_equipments = fields.Many2many('quotation.equipment', string="Equipments", copy=True)
    selected_quotation_spare_parts = fields.Many2many('quotation.spare.part', string="Spare Parts", copy=True)
    selected_quotation_tools = fields.Many2many('quotation.tool', string="Tools", copy=True)

    def compute_proposal_details(self):
        for record in self:
            tasks, types, types_hours = record.generate_project_tasks()
            record.is_cleaning_service = types['cleaning']
            record.is_steam_service = types['steam']
            record.is_marble_service = types['marble']
            record.write({'is_cleaning_service_saved': types['cleaning']})
            record.write({'is_steam_service_saved': types['steam']})
            record.write({'is_marble_service_saved': types['marble']})
            if types['cleaning']:
                tools = self.env['quotation.tool'].search([('auto_add', '=', True)]).ids
                materials = self.env['quotation.cleaning.material'].search([('auto_add', '=', True)]).ids
                for tool in tools:
                    record.write({'selected_quotation_tools': [(4, tool)]})
                for material in materials:
                    record.write({'selected_quotation_cleaning_material': [(4, material)]})

            record.hours_of_cleaning_quick = types_hours['cleaning']
            record.hours_of_cleaning_misc = types_hours['misc']
            record.hours_of_steam = types_hours['steam']
            record.hours_of_marble = types_hours['marble']

    def generate_quotation_lines(self):
        lines = []

        # HouseKeeping Lines
        for line in self.house_keeping:
            lines.append(
                (0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.description_sale or '/',
                    'product_uom_qty': line.calculate_round,
                })
            )

        # Cleaning Order Lines
        for line in self.indoor_cleanings_all:
            if line.area_to_clean != 0:
                if not self.cleaning_customer_type:
                    raise ValidationError(_("You can't generate order lines without choosing specific customer type."))
                data_dict = {
                    'product_id': line.product_id.id,
                    'name': line.product_id.description_sale or '/',
                    'product_uom_qty': line.area_to_clean,
                }
                if line.with_furniture == 'yes':
                    data_dict['price_unit'] = line.product_id.list_price * 1.15
                lines.append(
                    (0, 0, data_dict)
                )
        for line in self.indoor_cleanings_restaurant:
            if line.area_to_clean != 0:
                if not self.cleaning_customer_type:
                    raise ValidationError(_("You can't generate order lines without choosing specific customer type."))
                data_dict = {
                    'product_id': line.product_id.id,
                    'name': line.product_id.description_sale or '/',
                    'product_uom_qty': line.area_to_clean,
                }
                if 'Kitchen' in line.name:
                    data_dict['price_unit'] = line.product_id.list_price * 1.10
                lines.append(
                    (0, 0, data_dict)
                )
        for line in self.indoor_items_by_width_and_length:
            if line.area_to_clean != 0:
                if not self.cleaning_customer_type:
                    raise ValidationError(_("You can't generate order lines without choosing specific customer type."))
                lines.append(
                    (0, 0, {
                        'product_id': line.product_id.id,
                        'name': line.product_id.description_sale or '/',
                        'product_uom_qty': line.area_to_clean,
                    })
                )
        for line in self.indoor_outside_yard_floor:
            if line.area_to_clean != 0:
                if not self.cleaning_customer_type:
                    raise ValidationError(_("You can't generate order lines without choosing specific customer type."))
                lines.append(
                    (0, 0, {
                        'product_id': line.product_id.id,
                        'name': line.product_id.description_sale or '/',
                        'product_uom_qty': line.area_to_clean,
                    })
                )
        for line in self.indoor_curtains:
            if line.area_to_clean != 0:
                lines.append(
                    (0, 0, {
                        'product_id': line.product_id.id,
                        'name': line.product_id.description_sale or '/',
                        'product_uom_qty': line.area_to_clean,
                    })
                )
        for line in self.indoor_items_by_area:
            if line.area_to_clean != 0:
                lines.append(
                    (0, 0, {
                        'product_id': line.product_id.id,
                        'name': line.product_id.description_sale or '/',
                        'product_uom_qty': line.area_to_clean,
                    })
                )
        for line in self.indoor_external_facades:
            if line.area_to_clean != 0:
                lines.append(
                    (0, 0, {
                        'product_id': line.product_id.id,
                        'name': line.product_id.description_sale or '/',
                        'product_uom_qty': line.area_to_clean,
                    })
                )
        for line in self.indoor_items_by_piece:
            lines.append(
                (0, 0, {
                    'product_id': line.name.id,
                    'name': line.name.description_sale or '/',
                    'product_uom_qty': line.quantity,
                })
            )

        # Cleaning Misc. Lines
        for line in self.misc_cleaning_porcelain_ceramic:
            lines.append(
                (0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.description_sale or '/',
                    'product_uom_qty': line.area_to_clean,
                })
            )
        for line in self.misc_cleaning_marble:
            lines.append(
                (0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.description_sale or '/',
                    'product_uom_qty': line.area_to_clean,
                })
            )
        for line in self.misc_cleaning_parkay:
            lines.append(
                (0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.description_sale or '/',
                    'product_uom_qty': line.area_to_clean,
                })
            )
        for line in self.misc_cleaning_windows_shutter:
            lines.append(
                (0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.description_sale or '/',
                    'product_uom_qty': line.area_to_clean,
                })
            )
        for line in self.misc_cleaning_windows:
            lines.append(
                (0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.description_sale or '/',
                    'product_uom_qty': line.area_to_clean,
                })
            )
        for line in self.misc_cleaning_removal_window_frame:
            lines.append(
                (0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.description_sale or '/',
                    'product_uom_qty': line.linear_m,
                })
            )
        for line in self.misc_cleaning_service_items:
            lines.append(
                (0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.description_sale or '/',
                    'product_uom_qty': line.time_in_hours,
                })
            )
        for line in self.misc_cleaning_3rd_party_items:
            lines.append(
                (0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.description_sale or '/',
                    'product_uom_qty': 1,
                    'price_unit': line.cost_in_sr,
                })
            )
        for line in self.misc_cleaning_painted_walls_wallpapers:
            lines.append(
                (0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.description_sale or '/',
                    'product_uom_qty': line.area_to_clean,
                })
            )
        for line in self.misc_cleaning_miscellaneous_item:
            lines.append(
                (0, 0, {
                    'product_id': line.name.id,
                    'name': line.name.description_sale or '/',
                    'product_uom_qty': line.qty,
                })
            )

        # Steam Data
        for line in self.steam_cleaning_mocket:
            lines.append(
                (0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.description_sale or '/',
                    'product_uom_qty': line.qty
                })
            )
        for line in self.steam_cleaning_carpets:
            lines.append(
                (0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.description_sale or '/',
                    'product_uom_qty': line.qty,
                })
            )
        for line in self.steam_cleaning_arabic_seat:
            lines.append(
                (0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.description_sale or '/',
                    'product_uom_qty': line.qty,
                    'price_unit': line.price + 5,
                })
            )
        for line in self.steam_cleaning_mattress:
            lines.append(
                (0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.description_sale or '/',
                    'product_uom_qty': line.qty,
                })
            )
        for line in self.steam_cleaning_curtains:
            lines.append(
                (0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.description_sale or '/',
                    'product_uom_qty': line.qty,
                    'price_unit': line.price,
                })
            )
        for line in self.steam_cleaning_miscellaneous:
            lines.append(
                (0, 0, {
                    'product_id': line.name.id,
                    'name': line.name.description_sale or '/',
                    'product_uom_qty': line.qty,
                })
            )

        # Marble Data
        for line in self.marble_cleaning_surface:
            lines.append(
                (0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.description_sale or '/',
                    'product_uom_qty': line.area,
                })
            )
        for line in self.marble_polishing_surface:
            lines.append(
                (0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.description_sale or '/',
                    'product_uom_qty': line.linear_m,
                })
            )
        for line in self.marble_protection_surface:
            lines.append(
                (0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.description_sale or '/',
                    'product_uom_qty': line.area,
                })
            )
        for line in self.marble_extra_items:
            lines.append(
                (0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.description_sale or '/',
                    'product_uom_qty': 1,
                    'price_unit': line.s_price
                })
            )
        for line in self.marble_miscellaneous_item:
            lines.append(
                (0, 0, {
                    'product_id': line.name.id,
                    'name': line.name.description_sale or '/',
                    'product_uom_qty': line.qty,
                })
            )

        return lines

    def generate_quotation(self):
        for record in self:
            order = {
                'date_order': fields.Datetime.now(),
                'partner_id': record.customer.id,
                'validity_date': record.date,
                'house_service_id': record.id,
                'order_line': record.generate_quotation_lines(),
            }
            if record.pricelist_id:
                order.update({'pricelist_id': record.pricelist_id.id})
            res = self.env['sale.order'].create(order)
            if res:
                record.sale_order_id = res
                record.state = 'quoted'

    def cancel_quotation(self):
        for record in self:
            record.project_id.unlink()

    def unlink_quotation(self):
        for record in self:
            if record.sale_order_id:
                record.sale_order_id.action_cancel()
            record.sale_order_id = False

    def generate_project_tasks(self):
        lines = {'cleaning': [], 'marble': []}
        types = {'cleaning': False, 'steam': False, 'marble': False}
        total_hours = {'cleaning': 0, 'misc': 0, 'steam': 0, 'marble': 0}

        # HouseKeeping Lines
        for line in self.house_keeping:
            # total_hours += line.number_of_workers * 8
            lines['cleaning'].append(
                (0, 0, {
                    'name': line.product_id.name,
                    'planned_hours': line.number_of_workers * 8,
                    'uom_id': line.product_id.uom_id.id,
                    'uom_quantity': line.number_of_workers
                })
            )

        # Cleaning Order Lines
        for line in self.indoor_cleanings_all:
            if line.area_to_clean != 0:
                types['cleaning'] = True
                total_hours['cleaning'] += line.time_in_hours
                lines['cleaning'].append(
                    (0, 0, {
                        'name': line.product_id.name + ' - ' + line.name,
                        'planned_hours': line.time_in_hours,
                        'uom_id': line.product_id.uom_id.id,
                        'uom_quantity': line.area_to_clean
                    })
                )

        for line in self.indoor_cleanings_restaurant:
            if line.area_to_clean != 0:
                types['cleaning'] = True
                total_hours['cleaning'] += line.time_in_hours
                lines['cleaning'].append(
                    (0, 0, {
                        'name': line.product_id.name + ' - ' + line.name,
                        'planned_hours': line.time_in_hours,
                        'uom_id': line.product_id.uom_id.id,
                        'uom_quantity': line.area_to_clean
                    })
                )

        for line in self.indoor_items_by_width_and_length:
            if line.area_to_clean != 0:
                types['cleaning'] = True
                total_hours['cleaning'] += line.time_in_hours
                lines['cleaning'].append(
                    (0, 0, {
                        'name': line.product_id.name + ' - ' + line.name,
                        'planned_hours': line.time_in_hours,
                        'uom_id': line.product_id.uom_id.id,
                        'uom_quantity': line.area_to_clean
                    })
                )

        for line in self.indoor_outside_yard_floor:
            if line.area_to_clean != 0:
                types['cleaning'] = True
                total_hours['cleaning'] += line.time_in_hours
                lines['cleaning'].append(
                    (0, 0, {
                        'name': line.product_id.name + ' - ' + line.name,
                        'planned_hours': line.time_in_hours,
                        'uom_id': line.product_id.uom_id.id,
                        'uom_quantity': line.area_to_clean
                    })
                )

        for line in self.indoor_curtains:
            if line.area_to_clean != 0:
                types['cleaning'] = True
                total_hours['cleaning'] += line.time_in_hours
                lines['cleaning'].append(
                    (0, 0, {
                        'name': line.product_id.name + ' - ' + line.name,
                        'planned_hours': line.time_in_hours,
                        'uom_id': line.product_id.uom_id.id,
                        'uom_quantity': line.area_to_clean
                    })
                )

        for line in self.indoor_items_by_area:
            if line.area_to_clean != 0:
                types['cleaning'] = True
                total_hours['cleaning'] += line.time_in_hours
                lines['cleaning'].append(
                    (0, 0, {
                        'name': line.product_id.name + ' - ' + line.name,
                        'planned_hours': line.time_in_hours,
                        'uom_id': line.product_id.uom_id.id,
                        'uom_quantity': line.area_to_clean
                    })
                )

        for line in self.indoor_external_facades:
            if line.area_to_clean != 0:
                types['cleaning'] = True
                total_hours['cleaning'] += line.time_in_hours
                lines['cleaning'].append(
                    (0, 0, {
                        'name': line.product_id.name + ' - ' + line.name,
                        'planned_hours': line.time_in_hours,
                        'uom_id': line.product_id.uom_id.id,
                        'uom_quantity': line.area_to_clean
                    })
                )

        for line in self.indoor_items_by_piece:
            types['cleaning'] = True
            total_hours['cleaning'] += line.time_in_hours
            lines['cleaning'].append(
                (0, 0, {
                    'name': 'Items by piece - ' + line.name.name,
                    'planned_hours': line.time_in_hours,
                    'uom_id': line.name.uom_id.id,
                    'uom_quantity': line.quantity
                })
            )

        # Cleaning Misc. Lines
        for line in self.misc_cleaning_porcelain_ceramic:
            types['cleaning'] = True
            total_hours['misc'] += line.time_in_hours
            lines['cleaning'].append(
                (0, 0, {
                    'name': line.product_id.name + ' - ' + line.name,
                    'planned_hours': line.time_in_hours,
                    'uom_id': line.product_id.uom_id.id,
                    'uom_quantity': line.area_to_clean
                })
            )

        for line in self.misc_cleaning_marble:
            types['cleaning'] = True
            total_hours['misc'] += line.time_in_hours
            lines['cleaning'].append(
                (0, 0, {
                    'name': line.product_id.name + ' - ' + line.name,
                    'planned_hours': line.time_in_hours,
                    'uom_id': line.product_id.uom_id.id,
                    'uom_quantity': line.area_to_clean
                })
            )

        for line in self.misc_cleaning_parkay:
            types['cleaning'] = True
            total_hours['misc'] += line.time_in_hours
            lines['cleaning'].append(
                (0, 0, {
                    'name': line.product_id.name + ' - ' + line.name,
                    'planned_hours': line.time_in_hours,
                    'uom_id': line.product_id.uom_id.id,
                    'uom_quantity': line.area_to_clean
                })
            )

        for line in self.misc_cleaning_windows_shutter:
            types['cleaning'] = True
            total_hours['misc'] += line.time_in_hours
            lines['cleaning'].append(
                (0, 0, {
                    'name': line.product_id.name + ' - ' + line.name,
                    'planned_hours': line.time_in_hours,
                    'uom_id': line.product_id.uom_id.id,
                    'uom_quantity': line.area_to_clean
                })
            )

        for line in self.misc_cleaning_windows:
            types['cleaning'] = True
            total_hours['misc'] += line.time_in_hours
            lines['cleaning'].append(
                (0, 0, {
                    'name': line.product_id.name + ' - ' + line.name,
                    'planned_hours': line.time_in_hours,
                    'uom_id': line.product_id.uom_id.id,
                    'uom_quantity': line.area_to_clean
                })
            )

        for line in self.misc_cleaning_removal_window_frame:
            types['cleaning'] = True
            total_hours['misc'] += line.time_in_hours
            lines['cleaning'].append(
                (0, 0, {
                    'name': line.product_id.name + ' - ' + line.name,
                    'planned_hours': line.time_in_hours,
                    'uom_id': line.product_id.uom_id.id,
                    'uom_quantity': line.linear_m
                })
            )
        # PRODUCT OF SERVICE ITEMS
        # FIX ME
        for line in self.misc_cleaning_service_items:
            types['cleaning'] = True
            total_hours['misc'] += line.time_in_hours
            lines['cleaning'].append(
                (0, 0, {
                    'name': 'Dareed Service Item - ' + line.name,
                    'planned_hours': line.time_in_hours,
                    'uom_id': line.product_id.uom_id.id,
                    'uom_quantity': 1
                })
            )

        for line in self.misc_cleaning_painted_walls_wallpapers:
            types['cleaning'] = True
            total_hours['misc'] += line.time_in_hours
            lines['cleaning'].append(
                (0, 0, {
                    'name': line.product_id.name + ' - ' + line.name,
                    'planned_hours': line.time_in_hours,
                    'uom_id': line.product_id.uom_id.id,
                    'uom_quantity': line.area_to_clean
                })
            )

        if self.misc_cleaning_3rd_party_items:
            types['cleaning'] = True

        for line in self.misc_cleaning_miscellaneous_item:
            types['cleaning'] = True
            time_in_hours = line.time_in_mins / 60                      # 20 = (1 / 60) * 1 -> 1 is number of workers
            total_hours['cleaning'] += time_in_hours
            lines['cleaning'].append(
                (0, 0, {
                    'name': 'Cleaning Misc. Miscellaneous - ' + line.name.name,
                    'planned_hours': time_in_hours,
                    'uom_id': line.name.uom_id.id,
                    'uom_quantity': line.qty
                })
            )

        # Steam Data
        for line in self.steam_cleaning_mocket:
            types['steam'] = True
            time_in_hours = line.time_in_mins / 20                      # 20 = (1 / 60) * 3 -> 3 is number of workers
            total_hours['steam'] += time_in_hours
            lines['cleaning'].append(
                (0, 0, {
                    'name': line.product_id.name + ' - ' + line.name,
                    'planned_hours': time_in_hours,
                    'uom_id': line.product_id.uom_id.id,
                    'uom_quantity': line.qty
                })
            )

        for line in self.steam_cleaning_carpets:
            types['steam'] = True
            time_in_hours = line.time_in_mins / 20                      # 20 = (1 / 60) * 3 -> 3 is number of workers
            total_hours['steam'] += time_in_hours
            lines['cleaning'].append(
                (0, 0, {
                    'name': line.product_id.name + ' - ' + line.name,
                    'planned_hours': time_in_hours,
                    'uom_id': line.product_id.uom_id.id,
                    'uom_quantity': line.qty
                })
            )

        for line in self.steam_cleaning_arabic_seat:
            types['steam'] = True
            time_in_hours = line.time_in_mins / 20                      # 20 = (1 / 60) * 3 -> 3 is number of workers
            total_hours['steam'] += time_in_hours
            lines['cleaning'].append(
                (0, 0, {
                    'name': line.product_id.name + ' - ' + line.name,
                    'planned_hours': time_in_hours,
                    'uom_id': line.product_id.uom_id.id,
                    'uom_quantity': line.qty
                })
            )

        for line in self.steam_cleaning_mattress:
            types['steam'] = True
            time_in_hours = line.time_in_mins / 20                      # 20 = (1 / 60) * 3 -> 3 is number of workers
            total_hours['steam'] += time_in_hours
            lines['cleaning'].append(
                (0, 0, {
                    'name': line.product_id.name + ' - ' + line.name,
                    'planned_hours': time_in_hours,
                    'uom_id': line.product_id.uom_id.id,
                    'uom_quantity': line.qty
                })
            )

        for line in self.steam_cleaning_curtains:
            types['steam'] = True
            time_in_hours = line.time_in_mins / 20                      # 20 = (1 / 60) * 3 -> 3 is number of workers
            total_hours['steam'] += time_in_hours
            lines['cleaning'].append(
                (0, 0, {
                    'name': line.product_id.name + ' - ' + line.name,
                    'planned_hours': time_in_hours,
                    'uom_id': line.product_id.uom_id.id,
                    'uom_quantity': line.qty
                })
            )

        for line in self.steam_cleaning_miscellaneous:
            types['steam'] = True
            time_in_hours = line.time_in_mins / 20                      # 20 = (1 / 60) * 3 -> 3 is number of workers
            total_hours['steam'] += time_in_hours
            lines['cleaning'].append(
                (0, 0, {
                    'name': 'Steam Miscellaneous - ' + line.name.name,
                    'planned_hours': time_in_hours,
                    'uom_id': line.name.uom_id.id,
                    'uom_quantity': line.qty
                })
            )
        if total_hours['steam'] > 0:
            total_hours['steam'] += 1.5
            lines['cleaning'].append(
                (0, 0, {
                    'name': 'Steam Installment',
                    'planned_hours': 1.5,
                    'uom_id': False,
                    'uom_quantity': 1,
                })
            )
        if types['cleaning'] or types['steam']:
            if self.hours_of_cleaning_risk_hours or self.hours_of_steam_risk_hours:
                lines['cleaning'].append(
                    (0, 0, {
                        'name': 'Cleaning & Steam Risk Hours',
                        'planned_hours': self.hours_of_cleaning_risk_hours + self.hours_of_steam_risk_hours,
                        'uom_quantity': 1
                    })
                )

        # Marble Data
        for line in self.marble_cleaning_surface:
            types['marble'] = True
            total_hours['marble'] += line.time_in_hours
            lines['marble'].append(
                (0, 0, {
                    'name': line.product_id.name + ' - ' + line.name,
                    'planned_hours': line.time_in_hours,
                    'uom_id': line.product_id.uom_id.id,
                    'uom_quantity': line.area
                })
            )

        for line in self.marble_polishing_surface:
            types['marble'] = True
            total_hours['marble'] += line.time_in_hours
            lines['marble'].append(
                (0, 0, {
                    'name': line.product_id.name + ' - ' + line.name,
                    'planned_hours': line.time_in_hours,
                    'uom_id': line.product_id.uom_id.id,
                    'uom_quantity': line.linear_m
                })
            )

        for line in self.marble_protection_surface:
            types['marble'] = True
            total_hours['marble'] += line.time_in_hours
            lines['marble'].append(
                (0, 0, {
                    'name': line.product_id.name + ' - ' + line.name,
                    'planned_hours': line.time_in_hours,
                    'uom_id': line.product_id.uom_id.id,
                    'uom_quantity': line.area
                })
            )

        if self.marble_extra_items:
            types['marble'] = True

        for line in self.marble_miscellaneous_item:
            types['marble'] = True
            time_in_hours = line.time_in_mins / 60                      # 20 = (1 / 60) * 1 -> 1 is number of workers
            total_hours['marble'] += time_in_hours
            lines['marble'].append(
                (0, 0, {
                    'name': 'Marble Miscellaneous - ' + line.name.name,
                    'planned_hours': time_in_hours,
                    'uom_id': line.name.uom_id.id,
                    'uom_quantity': line.qty
                })
            )

        if types['marble']:
            if self.hours_of_marble_risk_hours:
                lines['marble'].append(
                    (0, 0, {
                        'name': 'Marble Risk Hours',
                        'planned_hours': self.hours_of_marble_risk_hours,
                        'uom_quantity': 1
                    })
                )

        return [lines, types, total_hours]

    def generate_project(self):
        self.ensure_one()
        tasks, types, total_hours = self.generate_project_tasks()
        if types['cleaning'] or types['steam']:
            flag = ''
            if types['cleaning']:
                flag += ' - Cleaning'
            if types['steam']:
                if flag:
                    flag += ' & Steam'
                else:
                    flag += ' - Steam'
            project = {
                'name': self.name + flag,
                'partner_id': self.customer.id,
                'service_id': self.id,
                'company_id': self.env.user.company_id.id,
                'is_cleaning_service': types['cleaning'],
                'is_steam_service': types['steam'],
                'is_marble_service': False,
                'contracts': self.contracts,
                'total_planned_days': self.total_duration_days,
                'task_ids': tasks['cleaning'],
                'total_planned_hours': self.hours_of_cleaning_total + self.hours_of_steam_total
            }
            res = self.env['project.project'].create(project)
            if res:
                self.project_id = res
        if types['marble']:
            project = {
                'name': self.name + ' - Marble',
                'partner_id': self.customer.id,
                'service_id': self.id,
                'company_id': self.env.user.company_id.id,
                'is_cleaning_service': False,
                'is_steam_service': False,
                'is_marble_service': types['marble'],
                'contracts': self.contracts,
                'total_planned_days': self.total_duration_days,
                'task_ids': tasks['marble'],
                'total_planned_hours': self.hours_of_marble_total
            }
            res = self.env['project.project'].create(project)
            if res:
                self.project_marble_id = res

    def cancel_project(self):
        if self.project_id:
            self.project_id.task_ids.unlink()
            self.project_id.unlink()

    @api.onchange("cleaning_level_of_dirtiness")
    def validate_items_by_piece(self):
        for record in self:
            for line in record.indoor_items_by_piece:
                if line.level_of_dirt.id != line.name.level_of_dirt.id:
                    line.name = self.env['product.product'].search([('name', '=', line.name.name),
                                                                    ('level_of_dirt', '=', line.level_of_dirt.id)],
                                                                   limit=1)
