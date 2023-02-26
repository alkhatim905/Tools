# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime


class AccountInvoice(models.Model):
    _inherit = "account.move"

    project_id = fields.Many2one('project.project', string="Project Name")
    service_type_ids = fields.Many2many('service.type', string="Service Type")
    aging = fields.Integer(string="Aging", compute="_get_aging_days", store=True)
    aging_char = fields.Char(string="Aging", compute="_get_aging_days", store=True)

    def update_aging(self):
        invoices = self.env['account.move'].search([])
        for invoice in invoices:
            invoice._get_aging_days()

    @api.depends('invoice_date_due')
    def _get_aging_days(self):
        for record in self:
            if record.invoice_date_due:
                due = datetime.strptime(record.invoice_date_due.strftime('%Y%m%d'), '%Y%m%d')
                now = fields.Datetime.now()
                days_diff = (due - now).days
                record.aging = days_diff
                record.aging_char = str(days_diff)
