# Copyright 2013 Julius Network Solutions
# Copyright 2015 Clear Corp
# Copyright 2016 OpenSynergy Indonesia
# Copyright 2017 ForgeFlow S.L.
# Copyright 2018 Hibou Corp.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
class StockMove(models.Model):
    _inherit = "stock.picking"

    date_done = fields.Datetime('Date of Transfer', copy=False, readonly=False, help="Date at which the transfer has been processed or cancelled.")

    def _action_done(self):
        """Call `_action_done` on the `stock.move` of the `stock.picking` in `self`.
        This method makes sure every `stock.move.line` is linked to a `stock.move` by either
        linking them to an existing one or a newly created one.

        If the context key `cancel_backorder` is present, backorders won't be created.

        :return: True
        :rtype: bool
        """
        self._check_company()

        todo_moves = self.mapped('move_lines').filtered(
            lambda self: self.state in ['draft', 'waiting', 'partially_available', 'assigned', 'confirmed'])
        for picking in self:
            if picking.owner_id:
                picking.move_lines.write({'restrict_partner_id': picking.owner_id.id})
                picking.move_line_ids.write({'owner_id': picking.owner_id.id})
        todo_moves._action_done(cancel_backorder=self.env.context.get('cancel_backorder'))
        # self.write({'date_done': fields.Datetime.now(), 'priority': '0'})

        # if incoming moves make other confirmed/partially_available moves available, assign them
        done_incoming_moves = self.filtered(lambda p: p.picking_type_id.code == 'incoming').move_lines.filtered(
            lambda m: m.state == 'done')
        done_incoming_moves._trigger_assign()

        self._send_confirmation_email()
        return True

class StockMove(models.Model):
    _inherit = "stock.move"

    analytic_account_id = fields.Many2one(
        string="Analytic Account",
        comodel_name="account.analytic.account",
    )
    analytic_tag_ids = fields.Many2many("account.analytic.tag", string="Analytic Tags")

    other_account_id = fields.Many2one(
        'account.account', 'Other output Account', company_dependent=True,
        domain="[('company_id', '=', allowed_company_ids[0]), ('deprecated', '=', False)]", check_company=True,
        help="""When automated inventory valuation is enabled on a product category, this account will replacement of 
        output account with current value of the products.""", )
    flock_origin = fields.Many2one('res.country', 'Flock Origin',)
    flock_number = fields.Char('Flock Number',)
    chick_breed = fields.Char('Chick Breed', )
    avg_doc_weight = fields.Float('AVG DOC Weight')
    arrival_datetime = fields.Datetime('Arrival Datetime')



    def _prepare_account_move_line(
            self, qty, cost, credit_account_id, debit_account_id, description
    ):
        self.ensure_one()
        res = super(StockMove, self)._prepare_account_move_line(
            qty, cost, credit_account_id, debit_account_id, description
        )
        for line in res:
            if (
                    line[2]["account_id"]
                    != self.product_id.categ_id.property_stock_valuation_account_id.id
            ):
                # Add analytic account in debit line
                if self.analytic_account_id:
                    line[2].update({"analytic_account_id": self.analytic_account_id.id, })
                    if self.other_account_id:
                        line[2].update({"account_id": self.other_account_id.id, })
                    # Add analytic tags in debit line
                if self.analytic_tag_ids:
                    line[2].update(
                        {"analytic_tag_ids": [(6, 0, self.analytic_tag_ids.ids)]}
                    )
        return res

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        fields = super()._prepare_merge_moves_distinct_fields()
        fields.append("analytic_account_id")
        fields.append("other_account_id")
        return fields


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    analytic_account_id = fields.Many2one(related="move_id.analytic_account_id")
    other_account_id = fields.Many2one(
        'account.account', 'Other output Account', company_dependent=True,
        domain="[('company_id', '=', allowed_company_ids[0]), ('deprecated', '=', False)]", check_company=True,
        help="""When automated inventory valuation is enabled on a product category, this account will replacement of 
        output account with current value of the products.""", )

    flock_origin = fields.Many2one('res.country', 'Flock Origin', required=True,related="move_id.flock_origin")
    flock_number = fields.Char('Flock Number',related="move_id.flock_number")
    chick_breed = fields.Char('Chick Breed',related="move_id.chick_breed")
    avg_doc_weight = fields.Float('AVG DOC Weight', related="move_id.avg_doc_weight")
    arrival_datetime = fields.Datetime('Arrival Datetime', related="move_id.arrival_datetime")

