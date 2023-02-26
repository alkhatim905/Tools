from datetime import datetime
from odoo import models, fields, api, _


class StandardReportXlsx(models.AbstractModel):
    _name = 'report.project_status_report.report_project_status_excel'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objs):
        sheet = workbook.add_worksheet('Project Status')
        format1 = workbook.add_format({'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True,
                                       'align': 'vcenter', 'bold': True})
        format21 = workbook.add_format({'font_size': 10, 'align': 'center', 'right': True, 'left': True,
                                        'bottom': True, 'top': True, 'bold': True})
        format21_unbolded = workbook.add_format({'font_size': 10, 'align': 'center', 'right': True, 'left': True,
                                                 'bottom': True, 'top': True, 'bold': False})
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
        sheet.merge_range('A1:D2', 'Project Status: ' + str(datetime.now().strftime("%Y-%m-%d %H:%M %p")), format1)
        projects = data['projects']
        sheet.set_column(0, 0, 10)
        sheet.set_column(1, 1, 25)
        sheet.set_column(2, 2, 15)
        sheet.set_column(3, 3, 15)
        sheet.set_column(4, 4, 15)
        sheet.set_column(5, 5, 15)
        sheet.set_column(6, 6, 15)
        sheet.set_column(7, 7, 10)
        sheet.set_column(8, 8, 10)
        sheet.set_column(9, 9, 15)
        sheet.set_column(10, 10, 15)
        sheet.set_column(11, 11, 10)
        sheet.set_column(12, 12, 15)
        sheet.set_column(13, 13, 15)

        # Project Header
        header_index = 3
        sheet.write(header_index, 0, "Project ID", format21)
        sheet.write(header_index, 1, "Project Name", format21)
        sheet.write(header_index, 2, "Project Type", format21)
        sheet.write(header_index, 3, "Customer", format21)
        sheet.write(header_index, 4, "Estimated Workers", format21)
        sheet.write(header_index, 5, "Allocated Workers", format21)
        sheet.write(header_index, 6, "Consumed Workers", format21)
        sheet.write(header_index, 7, "Calculated Progress", format21)
        sheet.write(header_index, 8, "Progress", format21)
        sheet.write(header_index, 9, "Progress Status", format21)
        sheet.write(header_index, 10, "Expected Remaining Workers", format21)
        sheet.write(header_index, 11, "Days To Complete Project", format21)
        sheet.write(header_index, 12, "Project P&L", format21)
        sheet.write(header_index, 13, "Today Allocated", format21)
        sheet.write(header_index, 14, "Today Progress", format21)
        sheet.write(header_index, 15, "Today P&L", format21)
        sheet.write(header_index, 16, "Project Status", format21)
        sheet.write(header_index, 17, "Project Value", format21)

        data_index = header_index
        for project_id in projects:
            data_index += 1
            project = self.env['project.project'].browse(project_id)
            # Project Header Data
            state = "None"
            if project.is_cleaning_service or project.is_steam_service:
                state = "Cleaning & Steam"
            if project.is_marble_service:
                state = "Marble"
            if (project.is_cleaning_service or project.is_steam_service) and project.is_marble_service:
                state = "All"
            sheet.write(data_index, 0, project.id, format21_unbolded)
            sheet.write(data_index, 1, project.name, format21_unbolded)
            sheet.write(data_index, 2, state, format21_unbolded)
            sheet.write(data_index, 3, project.partner_id.name, format21_unbolded)
            sheet.write(data_index, 4, project.total_estimated_workers, format21_unbolded)
            sheet.write(data_index, 5, project.total_allocated_workers, format21_unbolded)
            today_allocated = (
                sum([
                    (allocation.allocation_qty + allocation.overtime)
                    for allocation in
                    project.project_allocation_ids.filtered(lambda a: a.date == fields.Datetime.now().date())
                ])
            )

            allocated_cleaning_basic_workers = sum([allocation.allocation_qty for allocation in
                                                    project.project_allocation_ids.filtered(
                                                        lambda a: a.project_type in ['cleaning', 'marble'] and a.date < fields.Datetime.now().date())])

            allocated_cleaning_overtime_workers = sum([allocation.overtime for allocation in
                                                       project.project_allocation_ids.filtered(
                                                           lambda a: a.project_type in ['cleaning', 'marble'] and a.date < fields.Datetime.now().date())])

            consumed = allocated_cleaning_basic_workers + allocated_cleaning_overtime_workers
            sheet.write(data_index, 6, consumed, format21_unbolded)

            if project.total_estimated_workers:
                calculated_progress = (consumed / project.total_estimated_workers) * 100
            else:
                calculated_progress = 0

            sheet.write(data_index, 7, str(round(calculated_progress, 2)) + ' %', format21_unbolded)
            sheet.write(data_index, 8, '{0:,.2f}'.format(abs(project.total_progress)) + ' %', format21_unbolded)

            progress_status = abs(project.total_progress) - calculated_progress
            sheet.write(data_index, 9, str(round(progress_status, 2)) + ' %', format21_unbolded)

            if abs(project.total_progress):
                expected_remaining_workers = consumed / abs(project.total_progress / 100) - consumed
            else:
                expected_remaining_workers = 0

            sheet.write(data_index, 10, round(expected_remaining_workers, 2), format21_unbolded)

            days_to_complete_project = expected_remaining_workers / 4
            sheet.write(data_index, 11, round(days_to_complete_project, 2), format21_unbolded)

            if project.total_estimated_workers and consumed:
                project_pnl = abs(project.total_progress) / (consumed / project.total_estimated_workers)
            else:
                project_pnl = 0.0
            sheet.write(data_index, 12, '{0:,.2f}'.format(project_pnl) + ' %', format21_unbolded)
            sheet.write(data_index, 13, today_allocated, format21_unbolded)
            today_progress = 100 * (
                sum([
                    (progress.progress_percent / 100) * (
                                progress.task_id.planned_hours / project.total_planned_hours) if
                    progress.task_id and project.total_planned_hours else 0
                    for progress in self.env['task.progress'].search([
                        ('date', '=', fields.Datetime.now().date()),
                        ('project_id', '=', project_id),
                    ])
                ])
            )
            if project.total_estimated_workers and today_allocated:
                today_pnl = (abs(today_progress) / (today_allocated / project.total_estimated_workers))
            else:
                today_pnl = 0.0
            sheet.write(data_index, 14, '{0:,.2f}'.format(abs(today_progress)) + ' %', format21_unbolded)
            sheet.write(data_index, 15, '{0:,.2f}'.format(today_pnl) + ' %', format21_unbolded)
            sheet.write(data_index, 16, dict(project._fields['state'].selection).get(project.state), format21_unbolded)
            amount = 'None'
            currency = ''
            if project.service_id and project.service_id.sale_order_id:
                amount = '{0:,.2f}'.format(project.service_id.sale_order_id.amount_total)
                if project.service_id and project.service_id.sale_order_id.currency_id:
                    currency = ' ' + project.service_id.sale_order_id.currency_id.symbol

            sheet.write(data_index, 17, amount + ' ' + currency, format21_unbolded)
