from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    @api.onchange('partner_id')
    def partner_onchange(self):
        for rec in self:
           for line in  rec.order_line:
            #   print("********here*********")
              line.write({'partner_id' :rec.partner_id})
              print("********here*********",line.partner_id.name)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('partner_id')
    def partner_onchange(self):
        for rec in self:
           for line in  rec.order_line:
              line.partner_id = rec.partner_id.id

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    partner_info = fields.Char()
    partner_id = fields.Many2one('res.partner')
     # @api.onchange('partner_id')
    def show_info(self):
        for rec in self:
            product_id = rec.product_id
            print('#######################333',rec.partner_id.name)
            info = {}
            last_po = rec.env['purchase.order.line'].search([('product_id','=',product_id.id),('partner_id','=',rec.partner_id.id),('id','!=',rec.id)],order='create_date desc',limit=1)
            last_so_partner = rec.env['sale.order.line'].search([('product_id','=',product_id.id),('partner_id','=',rec.partner_id.id),('id','!=',rec.id)],order='create_date desc',limit=1)
            last_so = rec.env['sale.order.line'].search([('product_id','=',product_id.id),('id','!=',rec.id)],order='create_date desc',limit=1)

            if last_po:
                info['po']=last_po.price_unit
            if last_so_partner:
                info['so_partner'] = last_so_partner.price_unit
            if last_so:
                info['so'] = last_so.price_unit
            info['product_cost'] = rec.product_id.standard_price
            return info



class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
   
    partner_id = fields.Many2one('res.partner' , compute="compute_partner")

    @api.depends("order_id.partner_id")
    def compute_partner(self):
        for rec in self:
            rec.partner_id = rec.order_id.partner_id.id


   