# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ServiceType(models.Model):
    _name = "service.type"

    name = fields.Char(string="Service Type")
