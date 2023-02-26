# Copyright 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrCurriculum(models.Model):
    """Added the details of the curriculum."""

    _name = 'hr.curriculum'
    _description = "Employee's Curriculum"

    name = fields.Char('Name', required=True)
    employee_id = fields.Many2one('hr.employee',
                                  string='Employee',
                                  required=True)
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    description = fields.Text('Description')
    partner_id = fields.Many2one('res.partner',
                                 'Partner',
                                 help="Employer, School, University, "
                                      "Certification Authority")
    location = fields.Char('Location', help="Location")
    expire = fields.Boolean('Expire', help="Expire", default=True)

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        if self.filtered(lambda c: c.end_date and c.start_date and c.start_date > c.end_date):
            raise ValidationError(_('The start date must be earlier than the end date.'))
