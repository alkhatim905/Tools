# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    def action_done(self):
        return super(StockPickingInherit,self.sudo()).action_done()