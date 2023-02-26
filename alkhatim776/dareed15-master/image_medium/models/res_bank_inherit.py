# -*- coding: utf-8 -*-

import re

import collections

from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.tools import pycompat


class BankInherit(models.Model):
    _inherit = 'res.bank'

    cid = fields.Char('Client Identification')
    branch = fields.Integer('Branch')