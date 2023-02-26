# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime


class AccountMove(models.Model):
    _inherit = "account.move"

    followup_ids = fields.Many2many('invoice.followup', string="Invoice Follow-Up")
