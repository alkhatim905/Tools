from odoo import models, fields, api
import json
from odoo.tools import date_utils


class StockReport(models.TransientModel):
    _name = "wizard.product.card"
    _description = "Stock Product Report"

    product = fields.Many2one('product.product', string="Product", required=True)
    warehouses = fields.Many2many('stock.warehouse', string="Warehouse", required=True)
    locations = fields.Many2many('stock.location', string="Locations", required=True)
    start_date = fields.Datetime(string="Start Date", required=True)
    end_date = fields.Datetime(string="End Date", required=True)

    @api.onchange('warehouses')
    def _set_locations_domain(self):
        self.ensure_one()
        locations = list()
        if not self.warehouses:
            return {'domain': {'locations': [('id', '!=', False)]}}
        else:
            for warehouse in self.warehouses:
                locations += self.env['stock.location'].search([('location_id', '=', warehouse.view_location_id.id)]).ids
            return {'domain': {'locations': [('id', 'in', locations)]}}

    def export_xls(self):
        data = dict()
        data['product'] = self.product.id
        data['locations'] = list()
        if self.locations:
            data['locations'] = self.locations.ids
        elif self.warehouses:
            for warehouse in self.warehouses:
                data['locations'] += self.env['stock.location'].search(
                    [('location_id', '=', warehouse.view_location_id.id)]).ids
        else:
            data['locations'] += self.env['stock.location'].search([]).ids
        data['locations_names'] = ''
        for location in data['locations']:
            obj = self.env['stock.location'].browse(location)
            data['locations_names'] += obj.name + ', '
        data['product_name'] = self.product.name
        data['start_date'] = str(self.start_date)
        data['end_date'] = str(self.end_date)
        print("data-----------------",data)
       

        return {
            'data': data,
            'type': 'ir.actions.report',
            'report_name': 'product_card_report.report_product_card_excel',
            'report_type': 'xlsx',
            'report_file': self.product.name + " - Card Report.xlsx",
        }
        