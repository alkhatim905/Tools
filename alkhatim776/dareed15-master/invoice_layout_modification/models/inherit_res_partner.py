# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InheritResPartner(models.Model):
    _inherit = 'res.partner'

    building_no = fields.Char('Building No.')
    district = fields.Char('District')
    additional_no = fields.Char('Additional No.')
    other_seller_id = fields.Char('Other Seller ID')
