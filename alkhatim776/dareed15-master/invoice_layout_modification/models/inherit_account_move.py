# -*- coding: utf-8 -*-

from odoo import models, fields, api
import werkzeug.urls
import qrcode
from io import BytesIO
import base64
from datetime import datetime

class AccountMove(models.Model):
    _inherit = 'account.move'

    delivery_date = fields.Date(string="Delivery date")
    invoice_date_time = fields.Datetime(compute="compute_invoice_date_time")
    total_discount = fields.Float(string="Total Discount", compute='compute_invoice_total_discount')

    @api.depends('invoice_date')
    def compute_invoice_date_time(self):
        for rec in self:
            rec.invoice_date_time = datetime.strptime(
                str(self.date_invoice)+' '+str(self.create_date.time()), '%Y-%m-%d %H:%M:%S.%f')

    def compute_invoice_total_discount(self):
        for record in self:
            total = 0
            for line in record.invoice_line_ids:
                total += line.discount
            record.total_discount = total

    qr_code = fields.Binary(string="QR", attachment=True, store=True)

    def generate_qr(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.build_qr_code_data())
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_image = base64.b64encode(temp.getvalue())
        self.qr_code = qr_image

    def get_qr_encoding(self, tag, field):
        company_name_byte_array = field.encode('UTF-8')
        company_name_tag_encoding = tag.to_bytes(length=1, byteorder='big')
        company_name_length_encoding = len(
            company_name_byte_array).to_bytes(length=1, byteorder='big')
        return company_name_tag_encoding + company_name_length_encoding + company_name_byte_array

    def build_qr_code_data(self):
        seller_name_enc = self.get_qr_encoding(1, self.company_id.display_name)
        company_vat_enc = self.get_qr_encoding(2, self.company_id.vat)
        time_sa = fields.Datetime.context_timestamp(
            self.with_context(tz='Asia/Riyadh'), self.invoice_date_time)
        timestamp_enc = self.get_qr_encoding(3, time_sa.isoformat())
        invoice_total_enc = self.get_qr_encoding(4, str(self.amount_total))
        total_vat_enc = self.get_qr_encoding(
            5, str(self.currency_id.round(self.amount_total - self.amount_untaxed)))

        str_to_encode = seller_name_enc + company_vat_enc + \
            timestamp_enc + invoice_total_enc + total_vat_enc
        qr_code_str = base64.b64encode(str_to_encode).decode('UTF-8')
        return qr_code_str
