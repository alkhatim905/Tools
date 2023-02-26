# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    expected_date = fields.Datetime("Expected Date", compute=False, readonly=False, store=True,
                                    oldname='commitment_date',
                                    help="Delivery date you can promise to the customer, computed from product lead times and from the shipping policy of the order.")

    @api.onchange('order_line.customer_lead', 'confirmation_date', 'order_line')
    def change_expected_date(self):
        for order in self:
            dates_list = []
            confirm_date = fields.Datetime.from_string(
                (order.confirmation_date or order.write_date) if order.state == 'sale' else fields.Datetime.now())
            for line in order.order_line.filtered(lambda x: x.state != 'cancel' and not x._is_delivery()):
                dt = confirm_date + timedelta(days=line.customer_lead or 0.0)
                dates_list.append(dt)
            if dates_list:
                order.expected_date = fields.Datetime.to_string(min(dates_list))

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if order.expected_date and order.picking_ids:
                for picking in order.picking_ids:
                    picking.write({'scheduled_date': order.expected_date})
        return res
