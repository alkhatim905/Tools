from collections import defaultdict
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import format_date

class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'
    _description = 'Generate payslips for all selected employees'


    def _get_available_contracts_domain(self):
        print("kkfhkfhkhf")
        return [('contract_ids.state', 'in', ('open', 'close')),('company_id', '=', self.env.company.id),('contract_ids.branch_id', '=', self.env.user.branch_id.id )]

    @api.model
    def default_get(self, fields):
        res = super(HrPayslipEmployees, self).default_get(fields)
        # branch_id = False
        branch_id = False

        active_company = self.env['res.company']._company_default_get('hr.contract')
        branches = self.env['res.branch'].sudo().search([]).filtered(lambda m: m.company_id == active_company)

        if self.env.user.branch_id and branches:
            branch_id = self.env.user.branch_id.id

        res.update({
            'branch_id': branch_id,
            # 'warehouse_id': warehouse_id

        })

        return res

    def get_branches_domain(self):
        active_company = self.env['res.company']._company_default_get('hr.contract')
        branches = self.env['res.branch'].sudo().search([]).filtered(lambda m: m.company_id == active_company)

        domain = [('id', 'in', branches.ids)]
        return domain

    branch_id = fields.Many2one('res.branch', string="Branch", domain=get_branches_domain)

    # def _prepare_invoice(self):
    #     res = super(HrContract, self)._prepare_invoice()
    #     res['branch_id'] = self.branch_id.id
    #     return res

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        selected_brach = self.branch_id
        if selected_brach:
            user_id = self.env['res.users'].browse(self.env.uid)
            user_branch = user_id.sudo().branch_id
            if user_branch and user_branch.id != selected_brach.id:
                raise UserError(
                    "Please select active branch only. Other may create the Multi branch issue. \n\ne.g: If you wish to add other branch then Switch branch from the header and set that.")
