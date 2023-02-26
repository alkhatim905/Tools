# -*-	coding:	utf-8	-*-
from odoo import api, fields, models
import ast


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    overtime_group_ids = fields.Many2many('res.groups', 'overtime_sett_rel', 'sett_id',
                                                      'grp_id', 'Overtime Groups', )

    def set_values(self):
        set_param = self.env['ir.config_parameter'].set_param
        set_param('overtime_group_ids', (self.overtime_group_ids.ids))
        super(ResConfigSettings, self).set_values()

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        overtime_group_ids = self.env['ir.config_parameter'].sudo().get_param('overtime_group_ids')
        if overtime_group_ids:
            res.update(
                overtime_group_ids=ast.literal_eval(overtime_group_ids),
            )
        return res
