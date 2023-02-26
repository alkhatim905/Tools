# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import qrcode
import base64
import io
from odoo import http
from num2words import num2words
from odoo.tools.misc import formatLang, format_date, get_lang


class AccountMove(models.Model):
    _inherit = 'account.move'

    date_due = fields.Date('Date Due')
    invoice_date_supply = fields.Date('Date Of Supply')


    def change_size_page(self, items):

        paper_format = self.env['report.paperformat'].search([('id', '=', self.env.ref('e_tax_invoice_saudi_aio.paperformat_action_report_tax_invoice').id)])

        if len(items) > 3:
            paper_format.page_height = 240 + (len(items) * 7)



    def get_product_arabic_name(self,pid):
        translation = self.env['ir.translation'].search([
            ('name','=','product.product,name'),('state','=','translated'),
            ('res_id','=',pid)])
        if translation :
            return translation.value
        else: 
            product = self.env['product.product'].browse(int(pid))
            translation = self.env['ir.translation'].search([
                ('name','=','product.product,name'),('state','=','translated'),
                ('res_id','=',product.product_tmpl_id.id)])
            if translation :
                return translation.value
        return ''    

    def amount_word(self, amount):
        language = self.partner_id.lang or 'en'
        language_id = self.env['res.lang'].search([('code', '=', 'ar_001')])
        if language_id:
            language = language_id.iso_code
        amount_str =  str('{:2f}'.format(amount))
        amount_str_splt = amount_str.split('.')
        before_point_value = amount_str_splt[0]
        after_point_value = amount_str_splt[1][:2]           
        before_amount_words = num2words(int(before_point_value),lang=language)
        after_amount_words = num2words(int(after_point_value),lang=language)
        amount = before_amount_words + ' ' + after_amount_words
        return amount

    def amount_total_words(self, amount):
        words_amount = self.currency_id.amount_to_text(amount)
        return words_amount

    @api.model
    def get_qr_code(self):
        # base_url = http.request.env['ir.config_parameter'].get_param('web.base.url')
        # data = str(base_url) + str("/web#id="+str(self.id)+"&view_type=form&model="+self._name)     
        # data = 'Customer Name : ' + str(self.partner_id.name or '')
        # data += '\nVAT Number : ' + str(self.partner_id.vat or '')
        # data += '\nInvoice date : ' + str(self.invoice_date or '')
        # data += '\nTotal VAT : ' + str(self.amount_by_group and self.amount_by_group[0][3] or '')
        # data += '\nTotal Amount Due : ' + str(self.currency_id and self.currency_id.symbol or '') + ' ' + str(self.amount_residual or 0.0)
        data = 'Supplier Name : ' + str(self.company_id.name or '')
        data += '\nVAT Number : ' + str(self.company_id.vat or '')
        data += '\nCreate Datetime : ' + str(self.create_date.strftime("%Y-%m-%d %H:%M:%S") or '')
        data += '\nTotal VAT : ' + str(self.amount_tax)
        data += '\nTotal Amount Due : ' + str(self.currency_id and self.currency_id.symbol or '') + ' ' + str(self.amount_residual or '')                
        img = qrcode.make(data)
        result = io.BytesIO()
        img.save(result, format='PNG')
        result.seek(0)
        img_bytes = result.read()
        base64_encoded_result_bytes = base64.b64encode(img_bytes)
        base64_encoded_result_str = base64_encoded_result_bytes.decode('ascii')
        return base64_encoded_result_str

    def action_invoice_sent(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        self.ensure_one()
        template = self.env.ref('e_tax_invoice_saudi_aio.email_template_edi_invoice_etir', False)
        lang = get_lang(self.env)
        if template and template.lang:
            lang = template._render_template(template.lang, 'account.move', self.id)
        else:
            lang = lang.code
        compose_form = self.env.ref('account.account_invoice_send_wizard_form', raise_if_not_found=False)
        ctx = dict(
            default_model='account.move',
            default_res_id=self.id,
            # For the sake of consistency we need a default_res_model if
            # default_res_id is set. Not renaming default_model as it can
            # create many side-effects.
            default_res_model='account.move',
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
            custom_layout="mail.mail_notification_paynow",
            model_description=self.with_context(lang=lang).type_name,
            force_email=True
        )
        return {
            'name': _('Send Invoice'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice.send',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }


    # def action_invoice_sent(self):
    #     """ Open a window to compose an email, with the edi invoice template
    #         message loaded by default
    #     """
    #     self.ensure_one()
    #     template = self.env.ref('e_tax_invoice_saudi_aio.email_template_edi_invoice_etir', False)
    #     compose_form = self.env.ref('account.account_invoice_send_wizard_form', False)
    #     # have model_description in template language
    #     lang = self.env.context.get('lang')
    #     if template and template.lang:
    #         lang = template._render_template(template.lang, 'account.move', self.id)
    #     self = self.with_context(lang=lang)
    #     TYPES = {
    #         'out_invoice': _('Invoice'),
    #         'in_invoice': _('Vendor Bill'),
    #         'out_refund': _('Credit Note'),
    #         'in_refund': _('Vendor Credit note'),
    #     }
    #     ctx = dict(
    #         default_model='account.move',
    #         default_res_id=self.id,
    #         default_use_template=bool(template),
    #         default_template_id=template and template.id or False,
    #         default_composition_mode='comment',
    #         mark_invoice_as_sent=True,
    #         model_description=TYPES[self.type],
    #         custom_layout="mail.mail_notification_paynow",
    #         force_email=True
    #     )
    #     return {
    #         'name': _('Send Invoice'),
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'account.move.send',
    #         'views': [(compose_form.id, 'form')],
    #         'view_id': compose_form.id,
    #         'target': 'new',
    #         'context': ctx,
    #     }


class ResPartner(models.Model):
    _inherit = 'res.partner'

    building_no = fields.Char('Building No')
    additional_no = fields.Char('Additional No')
    other_seller_id = fields.Char('Other Seller Id')


class ResCompany(models.Model):
    _inherit = 'res.company'

    building_no = fields.Char(related='partner_id.building_no', store=True, readonly=False, string='Building No')
    additional_no = fields.Char(related='partner_id.additional_no', store=True, readonly=False, string='Additional No')
    other_seller_id = fields.Char(related='partner_id.other_seller_id', store=True, readonly=False, string='Other Seller Id')
    arabic_name = fields.Char('Name')
    arabic_street = fields.Char('Street')
    arabic_street2 = fields.Char('Street2')
    arabic_city = fields.Char('City')
    arabic_state = fields.Char('State')
    arabic_country = fields.Char('Country')
    arabic_zip = fields.Char('Zip')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def get_product_arabic_name(self,pid):
        translation = self.env['ir.translation'].search([
            ('name','=','product.product,name'),('state','=','translated'),
            ('res_id','=',pid)])
        if translation :
            return translation.value
        else: 
            product = self.env['product.product'].browse(int(pid))
            translation = self.env['ir.translation'].search([
                ('name','=','product.product,name'),('state','=','translated'),
                ('res_id','=',product.product_tmpl_id.id)])
            if translation :
                return translation.value
        return ''    

    @api.model
    def get_qr_code(self):
        # base_url = http.request.env['ir.config_parameter'].get_param('web.base.url')
        # data = str(base_url) + str("/web#id="+str(self.id)+"&view_type=form&model="+self._name)     
 
        data = 'Supplier Name : ' + str(self.company_id.name or '')
        data += '\nVAT Number : ' + str(self.company_id.vat or '')
        # data += '\nCreate Datetime : ' + str(self.create_date.strftime("%Y-%m-%d %H:%M:%S") or '')
        data += '\nDate Order : ' + str(self.date_order or '')
        data += '\nTotal VAT : ' + str(self.amount_tax or '')
        data += '\nTotal Amount : ' + str(self.currency_id and self.currency_id.symbol or '') + ' ' + str(self.amount_total or 0.0)
        img = qrcode.make(data)
        result = io.BytesIO()
        img.save(result, format='PNG')
        result.seek(0)
        img_bytes = result.read()
        base64_encoded_result_bytes = base64.b64encode(img_bytes)
        base64_encoded_result_str = base64_encoded_result_bytes.decode('ascii')
        return base64_encoded_result_str

    def amount_word(self, amount):
        language = self.partner_id.lang or 'en'
        language_id = self.env['res.lang'].search([('code', '=', 'ar_001')])
        if language_id:
            language = language_id.iso_code
        amount_str =  str('{:2f}'.format(amount))
        amount_str_splt = amount_str.split('.')
        before_point_value = amount_str_splt[0]
        after_point_value = amount_str_splt[1][:2]           
        before_amount_words = num2words(int(before_point_value),lang=language)
        after_amount_words = num2words(int(after_point_value),lang=language)
        amount = before_amount_words + ' ' + after_amount_words
        return amount

    def amount_total_words(self, amount):
        words_amount = self.company_id.currency_id.amount_to_text(amount)
        return words_amount


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def get_product_arabic_name(self,pid):
        translation = self.env['ir.translation'].search([
            ('name','=','product.product,name'),('state','=','translated'),
            ('res_id','=',pid)])
        if translation :
            return translation.value
        else: 
            product = self.env['product.product'].browse(int(pid))
            translation = self.env['ir.translation'].search([
                ('name','=','product.product,name'),('state','=','translated'),
                ('res_id','=',product.product_tmpl_id.id)])
            if translation :
                return translation.value
        return ''    

    @api.model
    def get_qr_code(self):
        # base_url = http.request.env['ir.config_parameter'].get_param('web.base.url')
        # data = str(base_url) + str("/web#id="+str(self.id)+"&view_type=form&model="+self._name)     
        # data = 'Vendor Name : ' + str(self.partner_id.name or '')
        # data += '\nVAT Number : ' + str(self.partner_id.vat or '')
        # data += '\nOrder date : ' + str(self.date_order or '')
        # data += '\nTotal VAT : ' + str(self.amount_tax or '')
        # data += '\nTotal Amount : ' + str(self.currency_id and self.currency_id.symbol or '') + ' ' + str(self.amount_total or 0.0)
        data = 'Supplier Name : ' + str(self.company_id.name or '')
        data += '\nVAT Number : ' + str(self.company_id.vat or '')
        # data += '\nCreate Datetime : ' + str(self.create_date.strftime("%Y-%m-%d %H:%M:%S") or '')
        data += '\nDate Order : ' + str(self.date_order or '')
        data += '\nTotal VAT : ' + str(self.amount_tax or '')
        data += '\nTotal Amount : ' + str(self.currency_id and self.currency_id.symbol or '') + ' ' + str(self.amount_total or 0.0)              
        img = qrcode.make(data)
        result = io.BytesIO()
        img.save(result, format='PNG')
        result.seek(0)
        img_bytes = result.read()
        base64_encoded_result_bytes = base64.b64encode(img_bytes)
        base64_encoded_result_str = base64_encoded_result_bytes.decode('ascii')
        return base64_encoded_result_str

    def amount_word(self, amount):
        language = self.partner_id.lang or 'en'
        language_id = self.env['res.lang'].search([('code', '=', 'ar_001')])
        if language_id:
            language = language_id.iso_code
        amount_str =  str('{:2f}'.format(amount))
        amount_str_splt = amount_str.split('.')
        before_point_value = amount_str_splt[0]
        after_point_value = amount_str_splt[1][:2]           
        before_amount_words = num2words(int(before_point_value),lang=language)
        after_amount_words = num2words(int(after_point_value),lang=language)
        amount = before_amount_words + ' ' + after_amount_words
        return amount

    def amount_total_words(self, amount):
        words_amount = self.company_id.currency_id.amount_to_text(amount)
        return words_amount