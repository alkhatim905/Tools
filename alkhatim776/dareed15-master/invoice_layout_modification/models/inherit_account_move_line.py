# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    tax_amount_per_line = fields.Float('Tax Amount', compute='compute_taxes_amount')

    @api.depends('move_id.invoice_line_ids')
    def compute_taxes_amount(self):
        for line in self:
            if line.invoice_line_tax_ids.price_include:
                tax_amount = 0.0
                if line.invoice_line_tax_ids:
                    for tax in line.invoice_line_tax_ids:
                        tax_amount += (line.price_unit * line.quantity) - (
                                    (line.price_unit * line.quantity) / (1 + (tax.amount / 100)))
                line.tax_amount_per_line = tax_amount
                print(line.price_unit * line.quantity, tax_amount)
            if not line.invoice_line_tax_ids.price_include:
                tax_amount = 0.0
                if line.invoice_line_tax_ids:
                    for tax in line.invoice_line_tax_ids:
                        tax_amount += (tax.amount * line.price_subtotal) / 100
                line.tax_amount_per_line = tax_amount
