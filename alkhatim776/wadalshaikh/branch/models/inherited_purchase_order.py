# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import Warning


class purchase_order(models.Model):

    _inherit = 'purchase.order.line'

    
    def _prepare_account_move_line(self, move=False):
        result = super(purchase_order, self)._prepare_account_move_line(move)
        result.update({
            'branch_id' : self.order_id.branch_id.id or False,
            
        })
        return result


    @api.model
    def default_get(self, default_fields):
        res = super(purchase_order, self).default_get(default_fields)
        branch_id = False
        active_company = self.env['res.company']._company_default_get('account.move')
        branches = self.env['res.branch'].sudo().search([]).filtered(lambda m: m.company_id == active_company)

        if self.env.user.branch_id and branches:
            branch_id = self.env.user.branch_id.id
        res.update({
            'branch_id': branch_id
        })

        return res

    def get_branches_domain(self):
        active_company = self.env['res.company']._company_default_get('purchase.order.line')
        branches = self.env['res.branch'].sudo().search([]).filtered(lambda m: m.company_id == active_company)

        domain = [('id', 'in', branches.ids)]
        return domain

    branch_id = fields.Many2one('res.branch', string="Branch", domain=get_branches_domain)

    def _prepare_stock_moves(self, picking):
        result = super(purchase_order, self)._prepare_stock_moves(picking)

        branch_id = False
        # if self.branch_id:
        #     branch_id = self.branch_id.id
        # elif self.env.user.branch_id:
        #     branch_id = self.env.user.branch_id.id
        #
        # for res in result:
        #     res.update({'branch_id' : branch_id})
        #
        active_company = self.env['res.company']._company_default_get('account.move')
        branches = self.env['res.branch'].sudo().search([]).filtered(lambda m: m.company_id == active_company)

        if self.env.user.branch_id and branches:
            branch_id = self.env.user.branch_id.id
        for res in result:
            res.update({'branch_id' : branch_id})

        return result


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    
    @api.model
    def default_get(self,fields):
        res = super(PurchaseOrder, self).default_get(fields)
        branch_id = picking_type_id = False

        active_company = self.env['res.company']._company_default_get('account.move')
        branches = self.env['res.branch'].sudo().search([]).filtered(lambda m: m.company_id == active_company)

        if self.env.user.branch_id and branches:
            branch_id = self.env.user.branch_id.id
        #
        # if self.env.user.branch_id:
        #     branch_id = self.env.user.branch_id.id
        
        if branch_id:
            branched_warehouse = self.env['stock.warehouse'].search([('branch_id','=',branch_id)])
            if branched_warehouse:
                picking_type_id = branched_warehouse[0].in_type_id.id
        else:
            picking = self._default_picking_type()
            picking_type_id = picking.id

        res.update({
            'branch_id' : branch_id,
            'picking_type_id' : picking_type_id
        })

        return res

    branch_id = fields.Many2one('res.branch', string='Branch')

    @api.model
    def _prepare_picking(self):
        res = super(PurchaseOrder, self)._prepare_picking()
        branch_id = False

        active_company = self.env['res.company']._company_default_get('account.move')
        branches = self.env['res.branch'].sudo().search([]).filtered(lambda m: m.company_id == active_company)

        if self.env.user.branch_id and branches:
            branch_id = self.env.user.branch_id.id

        # if self.branch_id:
        #     branch_id = self.branch_id.id
        #
        # if branch_id:
        #     branch_id = branch_id
        res.update({
            'branch_id' : branch_id
        })
        return res


    def _prepare_invoice(self):
        result = super(PurchaseOrder, self)._prepare_invoice()
        branch_id = False
        active_company = self.env['res.company']._company_default_get('account.move')
        branches = self.env['res.branch'].sudo().search([]).filtered(lambda m: m.company_id == active_company)

        if self.env.user.branch_id and branches:
            branch_id = self.env.user.branch_id.id
        # if branch_id:
        #     branch_id = branch_id
        #
        result.update({
                
                'branch_id' : branch_id
            })
        
        return result
    def action_view_invoice(self, invoices=False):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''

        result = super(PurchaseOrder, self).action_view_invoice(invoices)

        branch_id = False
        active_company = self.env['res.company']._company_default_get('account.move')
        branches = self.env['res.branch'].sudo().search([]).filtered(lambda m: m.company_id == active_company)

        if self.env.user.branch_id and branches:
            branch_id = self.env.user.branch_id.id

        result.update({
                
                'branch_id' : branch_id
            })
        

        return result

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        selected_brach = self.branch_id
        if selected_brach:
            user_id = self.env['res.users'].browse(self.env.uid)
            user_branch = user_id.sudo().branch_id
            if user_branch and user_branch.id != selected_brach.id:
                raise Warning("Please select active branch only. Other may create the Multi branch issue. \n\ne.g: If you wish to add other branch then Switch branch from the header and set that.")