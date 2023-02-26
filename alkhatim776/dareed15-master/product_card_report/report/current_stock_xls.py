from datetime import datetime
from odoo import models, _


class StandardReportXlsx(models.AbstractModel):
    _name = 'report.product_card_report.report_product_card_excel'
    _inherit = 'report.report_xlsx.abstract'

    def get_balance(self, data):
        print("hhhhhhhhhhhhhhhhhhhhhhhh")
        locations = tuple(data['locations'])
        self.env.cr.execute(
            """WITH
                source as (select t1.product_id, sum(t1.product_uom_qty) as openin from stock_move as t1
                where (t1.location_dest_id in %s)
                and t1.date < %s
                and t1.state = 'done'
                and t1.product_id = %s
                group by t1.product_id ),
                dist as (select t1.product_id, sum(t1.product_uom_qty) as openout from stock_move as t1
                where (t1.location_id in %s)
                and t1.date < %s
                and t1.state = 'done'
                and t1.product_id = %s
                group by t1.product_id),

                qtyin as (select t1.product_id, sum(t1.product_uom_qty) as qtyin from stock_move as t1
                where (t1.location_dest_id in %s)
                and t1.date BETWEEN %s AND %s
                and t1.state = 'done'
                and t1.product_id = %s
                group by t1.product_id ),

                qtyout as (select t1.product_id, sum(t1.product_uom_qty) as qtyout from stock_move as t1
                where (t1.location_id in %s)
                and t1.date BETWEEN %s AND %s
                and t1.state = 'done'
                and t1.product_id = %s
                group by t1.product_id)

                select (coalesce(source.openin,0) - coalesce(dist.openout,0)) as openBlance
                from dist full join source on dist.product_id = source.product_id
                full join qtyin on qtyin.product_id = source.product_id
                full join qtyout on qtyout.product_id = source.product_id
                left join product_product on product_product.id = GREATEST(dist.product_id,source.product_id,qtyin.product_id,qtyout.product_id)
                left join product_template on product_template.id = product_product.product_tmpl_id
                order by product_template.name""", (
                locations, data['start_date'], data['product'],
                locations, data['start_date'], data['product'],
                locations, data['start_date'], data['end_date'], data['product'],
                locations, data['start_date'], data['end_date'], data['product']))
        balances = self.env.cr.fetchall()
        return balances

    def get_lines(self, data):
        locations = tuple(data['locations'])
        self.env.cr.execute(
            """
            select 
                reference, 
                product_uom_qty, 
                t1.location_id, 
                t1.location_dest_id, 
                t1.date,
                t2.name 
            from 
                stock_move as t1 
                left join res_partner as t2 on t1.partner_id = t2.id
            where 
                (t1.location_dest_id in %s or t1.location_id in %s)
                and t1.date BETWEEN %s AND %s
                and t1.state = 'done'
                and t1.product_id = %s
            order by t1.date;
            """, (
                locations, locations,
                data['start_date'], data['end_date'],
                data['product'])
        )
        lines = self.env.cr.fetchall()
        return lines

    def generate_xlsx_report(self, workbook, data, objs):
        print("injjjjjjjjjjjjjjjjjjjjjjjjj")
        balances = self.get_balance(data)
        lines = self.get_lines(data)
        sheet = workbook.add_worksheet('Product Info')
        format1 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'vcenter',
             'bold': True})
        format11 = workbook.add_format(
            {'font_size': 12, 'align': 'center', 'right': True, 'left': True, 'bottom': True, 'top': True,
             'bold': True})
        format21 = workbook.add_format(
            {'font_size': 10, 'align': 'center', 'right': True, 'left': True, 'bottom': True, 'top': True,
             'bold': True})
        format21_unbolded = workbook.add_format(
            {'font_size': 10, 'align': 'center', 'right': True, 'left': True, 'bottom': True, 'top': True,
             'bold': False})
        format_left_align_left = workbook.add_format(
            {'font_size': 10, 'align': 'left', 'right': False, 'left': True, 'bottom': True, 'top': True,
             'bold': True})
        format_left_align_right = workbook.add_format(
            {'font_size': 10, 'align': 'left', 'right': True, 'left': False, 'bottom': True, 'top': True,
             'bold': True})
        format3 = workbook.add_format({'bottom': True, 'top': True, 'font_size': 12})
        font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 8})
        red_mark = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 8,
                                        'bg_color': 'red'})
        justify = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 12})
        format3.set_align('center')
        font_size_8.set_align('center')
        justify.set_align('justify')
        format1.set_align('center')
        red_mark.set_align('center')
        sheet.merge_range('A1:E3', 'Report Date: ' + str(datetime.now().strftime("%Y-%m-%d %H:%M %p")), format1)
        sheet.write(0, 5, 'From: ', format_left_align_left)
        sheet.merge_range('G1:I1', data['start_date'], format_left_align_right)
        sheet.write(1, 5, 'To: ', format_left_align_left)
        sheet.merge_range('G2:I2', data['end_date'], format_left_align_right)
        if data['locations_names']:
            sheet.write(2, 5, 'Locations: ', format_left_align_left)
            sheet.merge_range('G3:I3', data['locations_names'][:-2], format_left_align_right)

        sheet.set_column(0, 0, 15)
        sheet.set_column(1, 1, 15)
        sheet.set_column(2, 2, 15)
        sheet.set_column(3, 3, 15)
        sheet.set_column(4, 5, 15)
        sheet.set_column(4, 6, 15)
        sheet.set_column(4, 7, 15)

        sheet.write(3, 0, "Product", format21)
        sheet.merge_range('B4:G4', data['product_name'], format21)
        sheet.write(4, 0, "Reference", format21)
        sheet.write(4, 1, "Date", format21)
        sheet.write(4, 2, "From", format21)
        sheet.write(4, 3, "To", format21)
        sheet.write(4, 4, "Partner", format21)
        sheet.write(4, 5, "Open Balance", format21)
        sheet.write(4, 6, "Qty In", format21)
        sheet.write(4, 7, "Qty Out", format21)
        sheet.write(4, 8, "End Balance", format21)

        sheet.write(5, 0, '', format21_unbolded)
        sheet.write(5, 1, '', format21_unbolded)
        sheet.write(5, 2, '', format21_unbolded)
        sheet.write(5, 3, '', format21_unbolded)
        sheet.write(5, 4, '', format21_unbolded)
        if balances:
            sheet.write(5, 5, '{0:,.3f}'.format(balances[0][0]), format21)
        else:
            sheet.write(5, 5, '', format21)
        sheet.write(5, 6, '', format21_unbolded)
        sheet.write(5, 7, '', format21_unbolded)
        sheet.write(5, 8, '', format21_unbolded)

        count = 6
        if balances:
            open_balance = balances[0][0]
            end_balance = balances[0][0]
        else:
            open_balance = 0
            end_balance = 0
        for line in lines:
            x = line[4]
            qty_in = (line[1] if line[3] in data['locations'] else 0)
            qty_out = (line[1] if line[2] in data['locations'] else 0)
            from_location = self.env['stock.location'].browse(line[2])
            from_name = from_location[0].complete_name if from_location else '--'
            to_location = self.env['stock.location'].browse(line[3])
            to_name = to_location[0].complete_name if to_location else '--'
            end_balance = end_balance + qty_in - qty_out
            sheet.write(count, 0, line[0], format21_unbolded)
            sheet.write(count, 1, str(line[4].date()), format21_unbolded)
            sheet.write(count, 2, from_name, format21_unbolded)
            sheet.write(count, 3, to_name, format21_unbolded)
            sheet.write(count, 4, line[5], format21_unbolded)
            sheet.write(count, 5, '{0:,.3f}'.format(open_balance), format21_unbolded)
            sheet.write(count, 6, '{0:,.3f}'.format(qty_in), format21_unbolded)
            sheet.write(count, 7, '{0:,.3f}'.format(qty_out), format21_unbolded)
            sheet.write(count, 8, '{0:,.3f}'.format(end_balance), format21_unbolded)
            open_balance = end_balance
            count += 1

        sheet.write(count, 0, '', format21_unbolded)
        sheet.write(count, 1, '', format21_unbolded)
        sheet.write(count, 2, '', format21_unbolded)
        sheet.write(count, 3, '', format21_unbolded)
        sheet.write(count, 4, '', format21_unbolded)
        sheet.write(count, 5, '', format21_unbolded)
        sheet.write(count, 6, '', format21_unbolded)
        sheet.write(count, 7, '', format21_unbolded)
        sheet.write(count, 8, '{0:,.3f}'.format(end_balance), format21)
