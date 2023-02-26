from odoo import api, fields, models, _


class HouseKeepingTypeOfService(models.Model):
    _name = 'house.keeping.type.of.service'

    name = fields.Char(string="Type")
