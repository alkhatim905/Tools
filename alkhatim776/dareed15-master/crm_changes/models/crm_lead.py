from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CRMLead(models.Model):
    _inherit = "crm.lead"

    service_type_ids = fields.Many2many("crm.service.type", string="Service Type")
    area = fields.Float(string="Area")
    location_url = fields.Char(string="Location URL")
    calculation_sheet_ids = fields.One2many('house.service', 'lead_id', string="Calculation Sheet")
    calculation_sheet_count = fields.Integer(string="Calculation Sheet Count", compute="get_sheets_count")
    planned_revenue = fields.Monetary('Expected Revenue', currency_field='company_currency',
                                      track_visibility='always', compute='get_planned_revenue', store=False)

    def get_sheets_count(self):
        for record in self:
            record.calculation_sheet_count = len(record.calculation_sheet_ids)

    def generate_calculation_sheet(self):
        self.ensure_one()
        if not self.partner_id.id:
            raise ValidationError(_("Please Select a customer."))
        if not self.user_id.id:
            raise ValidationError(_("Please Select a salesperson."))
        vals = {
            'name': self.name,
            'customer': self.partner_id.id,
            'salesperson': self.user_id.id,
        }
        calculation_sheet = self.env['house.service'].create(vals)
        vals = {}
        if calculation_sheet:
            vals['calculation_sheet_ids'] = [(4, calculation_sheet.id)]
        stage = self.env['crm.stage'].search([('action_to_change', '=', 'inspected')], limit=1)
        if stage:
            vals['stage_id'] = stage.id
        self.write(vals)

    @api.depends('calculation_sheet_ids')
    def get_planned_revenue(self):
        for lead in self:
            if not lead.calculation_sheet_ids:
                lead.planned_revenue = 0.0
            else:
                sheet = lead.calculation_sheet_ids.sorted(key=lambda sheet: sheet.id, reverse=True)[0]
                if sheet.sale_order_id:
                    lead.planned_revenue = sheet.sale_order_id.amount_total
                    if sheet.project_id:
                        from_stage = ['quoted', 'inspected']
                        to_stage = 'won'
                    else:
                        from_stage = 'inspected'
                        to_stage = 'quoted'
                    if lead.stage_id.action_to_change in from_stage:
                        stage = self.env['crm.stage'].search([('action_to_change', '=', to_stage)], limit=1)
                        if stage:
                            lead.write({'stage_id': stage.id})
                else:
                    lead.planned_revenue = 0.0
                    if lead.stage_id.action_to_change == 'quoted':
                        stage = self.env['crm.stage'].search([('action_to_change', '=', 'inspected')], limit=1)
                        if stage:
                            lead.write({'stage_id': stage.id})
