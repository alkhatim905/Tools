# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime
import ast


class EmployeeOverTime(models.Model):
    _name = 'employee.overtime'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'

    name = fields.Char(string='Description', tracking=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('approved', 'Approved'), ('confirmed', 'Confirmed'), ('cancel', 'Canceled')],
        default='draft', copy=False, tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True)
    emp_code = fields.Char(string='Employee Code', related='employee_id.emp_code', store=1, tracking=True)
    image_medium = fields.Binary(related='employee_id.image_medium')
    expect_sign_out = fields.Float('Expect Sing out', tracking=True)
    act_sign_out = fields.Float('Actual Sing out', tracking=True)
    diff = fields.Float('Difference', compute='calculate_diff_hours', store=True, tracking=True)
    reason = fields.Selection(
        [('none', 'None'), ('business_need', 'Business Need'), ('no_business_need', 'No Business Need')],
        string="Reason", default='none')
    attend_id = fields.Many2one('hr.attendance')
    checkout_date = fields.Datetime('Checkout Date', related='attend_id.check_out', store=True)
    overtime_type = fields.Selection([('working_days', 'Working Day'), ('days_off', 'Days Off'),
                                      ('public_holiday', 'Public Holiday')], default='working_days', reqired=1)

    @api.model
    def create(self, values):
        res = super(EmployeeOverTime, self).create(values)
        ovt = str(datetime.timedelta(hours=res.diff)).rsplit(':', 1)[0]
        overtime_groups_ids = ast.literal_eval(
            (self.env['ir.config_parameter'].sudo().get_param('overtime_group_ids')))
        recipient_ids = []

        if res.employee_id.parent_id.address_home_id.id:
            recipient_ids.append(res.employee_id.parent_id.address_home_id.id)

        for group in self.env['res.groups'].search([('id', 'in', overtime_groups_ids)]):
            for user in group.users:
                if user.partner_id.id not in recipient_ids:
                    recipient_ids.append(user.partner_id.id)
        if ovt:
            mail_data = {'subject': 'New Overtime Created ',
                         'body_html': 'Dears' + ',<br/>' +
                                      'New overtime record has been created to employee ' + res.employee_id.name + " , Overtime hours " + ovt + "<br/>",
                         'recipient_ids': [(6, 0, recipient_ids)],
                         'author_id': self.env.ref('base.partner_admin').id,
                         }
            if recipient_ids:
                mail = self.env['mail.mail'].create(mail_data)
                mail.send()
        return res

    @api.depends('expect_sign_out', 'act_sign_out', 'employee_id')
    def calculate_diff_hours(self):
        for val in self:
            val.diff = val.act_sign_out - val.expect_sign_out

    def action_confirmed(self):
        for rec in self:
            if rec.reason == 'none':
                raise ValidationError(_('You must set reason to confirm !'))
            rec.state = 'confirmed'

    
    def action_approve(self):
        for rec in self:
            rec.state = 'approved'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
