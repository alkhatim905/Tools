from odoo import api, fields, models, _


class CleaningLevelOfDirtiness(models.Model):
    _name = "cleaning.level.of.dirtiness"

    name = fields.Char(string="Name")

