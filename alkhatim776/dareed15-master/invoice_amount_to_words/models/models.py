# -*- coding: utf-8 -*-

from odoo import models, fields, api
from decimal import Decimal
from num2words import num2words
from odoo.tools import float_is_zero

class ResCurrency(models.Model):
    _inherit = "res.currency"

    currency_subunit_label = fields.Char(translate=True)
    currency_unit_label = fields.Char(translate=True)


class AccountInvoice(models.Model):
    _inherit = "account.move"

    total_amount_words = fields.Char(string="Amount in Lettre", compute='_compute_amount' ,store=True)
    am_in_report = fields.Boolean("Show in invoice report", default= True)
    choose_lang = fields.Boolean("Choose a language...", default= True)
    lang = fields.Selection([
        ('en', 'English'),
        ('en_GB', 'English - Great Britain'),
        ('ar', 'Arabic'),
        ('de', 'German'),
        ('dk', 'Danish'),
        ('fr', 'French'),
        ('es', 'Spanish'),
        ('id', 'Indonesian'),
        ('lt', 'Lithuanian'),
        ('lv', 'Latvian'),
        ('no', 'Norwegian'),
        ('pl', 'Polish'),
        ('sl', 'Slovene'),
        ('ru', 'Russian'),
        ('tr', 'Turkish'),
        ('nl', 'Dutch'),
        ('uk', 'Ukrainian')
    ], "Language", default='en')

    @api.depends('invoice_line_ids.price_subtotal', 'currency_id', 'company_id', 'invoice_date','lang', 'choose_lang')
    def _compute_amount(self):
        super(AccountInvoice, self)._compute_amount()
        for record in self:
            amount = int(record.amount_total)
            amount_decimal = int(record.amount_total * 100 % 100)
            if record.choose_lang:
                try:
                    lang = self.env['res.lang'].search([('iso_code', '=', record.lang)], limit=1)
                    print("Lang = ", lang.code)
                    unit = self.env['ir.translation'].search([('lang', '=', lang.code),
                            ('src', '=', record.currency_id.currency_unit_label)], limit=1)

                    subunit = self.env['ir.translation'].search([('lang', '=', lang.code),
                            ('src', '=', record.currency_id.currency_subunit_label)], limit=1)
                    if not unit:
                        src = self.env['ir.translation'].search([
                            ('value', '=', record.currency_id.currency_unit_label)], limit=1).src

                        unit = self.env['ir.translation'].search([('lang', '=', lang.code),
                                                                  ('src', '=', src)],
                                                                 limit=1)
                        if not unit:
                            unit = self.env['ir.translation'].search([('src', '=', src)], limit=1)
                    if not subunit:
                        src = self.env['ir.translation'].search([
                            ('value', '=', record.currency_id.currency_subunit_label)], limit=1).src

                        subunit = self.env['ir.translation'].search([('lang', '=', lang.code),
                                                                  ('src', '=', src)],
                                                                 limit=1)
                        if not subunit:
                            subunit = self.env['ir.translation'].search([('src', '=', src)], limit=1)

                    print("Units = ", record.currency_id.currency_unit_label, record.currency_id.currency_subunit_label)
                    print("Units 2 = ", subunit.value, subunit.src)
                    if unit and subunit and unit.value and subunit.value:
                        if amount and amount_decimal:
                            record.total_amount_words = num2words(Decimal(str(amount)), lang=record.lang) + ' ' + \
                            (unit.value or unit.src) + ', ' + num2words(Decimal(str(amount_decimal)),
                            lang=record.lang) + ' ' + (subunit.value or subunit.src)
                        elif amount or not record.amount_total:
                            record.total_amount_words = num2words(Decimal(str(amount)), lang=record.lang) + ' ' + \
                                                        (unit.value or unit.src)
                        elif amount_decimal:
                            record.total_amount_words = num2words(Decimal(str(amount_decimal)),
                            lang=record.lang) + ' ' + (subunit.value or subunit.src)

                    elif record.currency_id.currency_unit_label and record.currency_id.currency_subunit_label:
                        if amount and amount_decimal:
                            record.total_amount_words = num2words(Decimal(str(amount)), lang=record.lang) + ' ' + \
                                (record.currency_id.currency_unit_label) + ', ' + num2words(Decimal(str(amount_decimal)),
                                lang=record.lang) + ' ' + (record.currency_id.currency_subunit_label)
                        elif amount or not record.amount_total:
                            record.total_amount_words = num2words(Decimal(str(amount)), lang=record.lang) + ' ' + \
                                (record.currency_id.currency_unit_label)
                        elif amount_decimal:
                            record.total_amount_words = num2words(Decimal(str(amount_decimal)),
                                lang=record.lang) + ' ' + (record.currency_id.currency_subunit_label)


                    else:
                        record.total_amount_words = num2words(Decimal(str(record.amount_total)), lang=record.lang) +' ' + str(record.currency_id.symbol)
                except NotImplementedError:
                    print("2222222222222222222222")
                    record.total_amount_words = num2words(Decimal(str(record.amount_total)), lang='en') +' ' + str(record.currency_id.symbol)
            else:
                print("22222222222222222222222222222")
                record.total_amount_words = num2words(Decimal(str(record.amount_total)), lang=record.env.user.lang)+ ' ' + str(record.currency_id.symbol)

        # ('en', 'English'),
        # ('ar', 'Arabic'),
        # ('cz', 'Czech'),
        # ('de', 'German'),
        # ('dk', 'Danish'),
        # ('en_GB', 'English - Great Britain'),
        # ('en_IN', 'English - India'),
        # ('es', 'Spanish'),
        # ('es_CO', 'Spanish - Colombia'),
        # ('es_VE', 'Spanish - Venezuela'),
        # ('fi', 'Finnish'),
        # ('fr', 'French'),
        # ('fr_CH', 'French - Switzerland'),
        # ('fr_BE', 'French - Belgium'),
        # ('fr_DZ', 'French - Algeria'),
        # ('he', 'Hebrew'),
        # ('id', 'Indonesian'),
        # ('ja', 'Japanese'),
        # ('ko', 'Korean'),
        # ('lt', 'Lithuanian'),
        # ('lv', 'Latvian'),
        # ('no', 'Norwegian'),
        # ('pl', 'Polish'),
        # ('pt', 'Portuguese'),
        # ('pt_BR', 'Portuguese - Brazilian'),
        # ('sl', 'Slovene'),
        # ('sr', 'Serbian'),
        # ('ro', 'Romanian'),
        # ('ru', 'Russian'),
        # ('tr', 'Turkish'),
        # ('vi', 'Vietnamese'),
        # ('nl', 'Dutch'),
        # ('uk', 'Ukrainian')
