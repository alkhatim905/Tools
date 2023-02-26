# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class InvoiceFollowUp(models.Model):
    _name = "invoice.followup"

    name = fields.Char(string="Name")
