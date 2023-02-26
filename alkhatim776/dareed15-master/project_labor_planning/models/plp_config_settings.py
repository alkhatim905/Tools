# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PLPConfigSettings(models.Model):
    _name = 'plp.config.settings'
    _description = 'Labor Planning Configuration'

    master_planner_sheet_range = fields.Integer(string="Master Planner Sheet Range", required=True)
    vacant_no_cleaning_staff = fields.Integer(string="Vacant No. Of Cleaning/Steam Staff", required=True)
    vacant_no_marble_staff = fields.Integer(string="Vacant No. Of Marble Staff", required=True)

    @api.constrains('master_planner_sheet_range','vacant_no_cleaning_staff','vacant_no_marble_staff')
    def _plp_constrain(self):
        if self.search_count([]) > 1:
            raise ValidationError(_('You can not create more than one record!'))