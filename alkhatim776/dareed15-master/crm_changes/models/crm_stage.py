from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CRMStage(models.Model):
    _inherit = "crm.stage"

    action_to_change = fields.Selection([
        ('inspected', 'Inspected'),
        ('quoted', 'Quoted'),
        ('won', 'Deal Won'),
    ], string="Action To Change")

    @api.constrains('action_to_change')
    def constrain_action_to_change(self):
        for record in self:
            if record.action_to_change:
                domain = [('action_to_change', '=', record.action_to_change)]
                if record.id:
                    domain.append(
                        ('id', '!=', record.id)
                    )
                alters = self.search(domain)
                if alters:
                    raise ValidationError(_("You can't create two stages with the same action to change '%s'."
                                            % dict(record._fields['action_to_change'].selection)
                                            .get(record.action_to_change)))
