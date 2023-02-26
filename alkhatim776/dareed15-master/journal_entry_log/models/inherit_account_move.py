# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import models, fields, api, _


class JournalEntry(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'mail.thread']

   
    @api.model
    def create(self, vals):
        move = super(JournalEntry, self).create(vals)
        move.log_message()
        return move

    def log_message(self):
        def _format_message(message_description, tracked_values):
            message = ''
            if message_description:
                message = '<span>%s</span>' % message_description
            for name, values in tracked_values.items():
                message += '<div> &nbsp; &nbsp; &bull; <b>%s</b>: ' % name
                message += '%s</div>' % values
            return message

        for line in self:
            if line:
                msg_values = {
                    'Created by': self.create_uid.name,
                    'Created on': self.create_date.strftime('%Y-%m-%dT%H:%M:%S'),
                    'Last Updated on': self.write_date.strftime('%Y-%m-%dT%H:%M:%S'),
                    'Last Updated by': self.write_uid.name}
                msg = _format_message(_('New Journal Entry Created.'), msg_values)
                line.message_post(body=msg)

   

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

  
    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='restrict', tracking=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',
        index=True, compute="_compute_analytic_account_id", store=True, readonly=False, check_company=True, copy=True,tracking=True)
    
    amount_currency = fields.Monetary(string='Amount in Currency', store=True, copy=True,tracking=True,
        help="The amount expressed in an optional other currency if it is a multi-currency entry.")    
    debit = fields.Monetary(string='Debit', default=0.0, currency_field='company_currency_id',tracking=True)

    credit = fields.Monetary(string='Credit', default=0.0, currency_field='company_currency_id',tracking=True)
    tax_ids = fields.Many2many(
    comodel_name='account.tax',
    string="Taxes",
    context={'active_test': False},
    check_company=True,
    tracking=True,
    help="Taxes that apply on the base amount")