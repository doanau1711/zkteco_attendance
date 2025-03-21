from datetime import datetime, timedelta

from pytz import timezone

from odoo import fields, models, api, exceptions, _
from odoo.exceptions import UserError
from odoo.tools import pytz
import pytz
import sys
import os
from zk import ZK
sys.path.insert(1,os.path.abspath("./pyzk"))

# pip install -U pyzk

class HrAttendanceTemporary(models.Model):
    _name = 'hr.attendance.temporary'
    _description = 'Hr Attendance Temporary'

    employee_id = fields.Many2one(
        comodel_name='hr.employee'
    )

    date_char = fields.Char(

    )

    check_in_char = fields.Char(

    )

    check_out_char = fields.Char(

    )

    check_in = fields.Datetime(


    )
    check_out = fields.Datetime(
    )


    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('done', 'Done'),
            ('error', 'Error')
        ],
        default='draft'
    )

    actual_work = fields.Float(
        compute='_compute_actual_work',
        store=True, readonly=True
    )

    @api.model
    def create(self, vals):
        check_in_char = vals.get('check_in_char') or None
        check_out_char = vals.get('check_out_char') or None
        if check_in_char and check_out_char:
            check_in_char_split = check_in_char.split(' ')
            check_out_char_split = check_out_char.split(' ')
            if len(check_in_char_split) > 1 and len(check_in_char_split) == len(check_out_char_split):

                    for i in range(len(check_in_char_split)-1):

                        vals['check_in_char'] = check_in_char.split(' ')[i]
                        vals['check_out_char'] = check_out_char.split(' ')[i]
                        self.create(vals)
                    vals['check_in_char'] = check_in_char.split(' ')[len(check_in_char_split)-1]
                    vals['check_out_char'] = check_out_char.split(' ')[len(check_in_char_split)-1]
            if len(check_in_char_split) != len(check_out_char_split):
                vals['state'] = 'error'
            if self.search([
                ('check_in_char', '=', check_in_char),
                ('check_out_char', '=', check_out_char),
                ('employee_id', '=', vals.get('employee_id')),
                ('date_char', '=', vals.get('date_char'))
            ]):
                vals['state'] = 'error'

        else:
            vals['state'] = 'error'

        return super(HrAttendanceTemporary, self).create(vals)

    # def write(self, vals):
    #     if self.state == 'done' and (vals.get('check_out') or vals.get('check_in')):
    #         raise UserError('State is done. Can not change check_in and check_out')
    #     res = super(HrAttendanceTemporary, self).write(vals)
    #
    #     return res

    #
    # def calculate_actual_work(self):
    #     for rec in self:
    #         if not rec.actual_work and rec.check_in and rec.check_out:
    #             rec.write({
    #                 'actual_work': (rec.check_out - rec.check_in).total_seconds() / 3600
    #             })

    error_message = fields.Char(

    )

    def import_to_attendance(self):
        attendance = self.env['hr.attendance']
        for rec in self:
            if rec.state != 'done' and rec.state != 'error' and rec.check_out and rec.check_in:

                attendance_same_check_in = attendance.search([
                    ('check_in', '=', rec.check_in),
                    ('employee_id', '=', rec.employee_id.id)
                ])
                if attendance_same_check_in:
                    if attendance_same_check_in.status == 'error':
                        attendance_same_check_in.write({
                            'check_out': rec.check_out,
                            'status': 'out of work'
                        })
                        rec.write({
                            'state': 'done'
                        })
                    elif attendance_same_check_in.status == 'out of work' and attendance_same_check_in.check_out == rec.check_out:
                        rec.write({
                            'state': 'done'
                        })
                else:
                    attendance_overlapped_time = attendance.search([
                        ('employee_id', '=', rec.employee_id.id),
                        ('check_in', '<=', rec.check_out),
                        ('check_out', '>=', rec.check_in),
                        ('status', '!=', 'error')
                    ])
                    if attendance_overlapped_time:
                        rec.write({
                            'state': 'error',
                            'error_message': 'Đã trùng'
                        })
                    else:
                        attendance.create({
                            'employee_id': rec.employee_id.id,
                            'check_in': rec.check_in,
                            'check_out': rec.check_out,
                            'status': 'out of work'
                        })
                        rec.write({
                            'state': 'done'
                        })


    def calculate_check_in_out(self):
        for rec in self.filtered(lambda x: x.state != 'error'):
            if rec.date_char and rec.check_in_char and rec.check_out_char:
                if rec.date_char.find('/') == -1:
                    rec.write({
                        'date_char': (datetime(1900, 1, 1) + timedelta(days=int(rec.date_char) - 2)).strftime('%d/%m/%Y')
                    })
                if rec.check_in_char.find(':') == -1:
                    check_in_float = float(rec.check_in_char) * 24
                    hour_char, minute_char = divmod(check_in_float, 1)
                    hour_char = f'{int(hour_char):02d}'
                    minute_char = f'{int(minute_char*60):02d}'
                    rec.write({
                        'check_in_char': str(hour_char + ':' + minute_char)
                    })
                if rec.check_out_char.find(':') == -1:
                    check_out_float = float(rec.check_out_char) * 24
                    hour_char, minute_char = divmod(check_out_float, 1)
                    hour_char = f'{int(hour_char):02d}'
                    minute_char = f'{int(minute_char*60):02d}'
                    rec.write({
                        'check_out_char': str(hour_char + ':' + minute_char)
                    })
                date_char = rec.date_char.split('/')
                # date_char = date_char[2] + '-' + date_char[1] + '-' + date_char[0]

                date_char = datetime(year=int(date_char[2]), month=int(date_char[1]), day=int(date_char[0]), minute=0, second=0, hour=0)
                check_out_float = rec.check_out_char.split(':')
                check_in_float = rec.check_in_char.split(':')
                date_in = date_char + timedelta(hours=int(check_in_float[0]), minutes=int(check_in_float[1]))
                date_out = date_char + timedelta(hours=int(check_out_float[0]), minutes=int(check_out_float[1]))
                if date_out < date_in:
                    date_out += timedelta(days=1)

                user_tz = pytz.timezone(self.env.user.tz)


                rec.write({
                    'check_in': user_tz.localize(date_in).astimezone(pytz.utc).replace(tzinfo=None),
                    'check_out': user_tz.localize(date_out).astimezone(pytz.utc).replace(tzinfo=None)
                })


                minimum_time = float(self.env['ir.config_parameter'].get_param('attendance_minimum_work_time') or 0)
                if (rec.check_out - rec.check_in).total_seconds() / 3600 < minimum_time:
                    rec.write({
                        'state': 'error'
                    })
                else:
                    rec.write({
                        'state': 'draft'
                    })

            else:
                rec.write({
                    'state': 'error'
                })

    # Copy from co_zkteco.py

    def call_api(self):

        attendance_list = []
        device_list = self.env['hr.biometric.device'].sudo().search([('active', '=', True)])
        for device in device_list:
            conn = None
            ip_char = device.ip
            port_char = device.port
            # create ZK instance
            zk = ZK(ip_char, port=int(port_char), timeout=5, password=0, force_udp=False, ommit_ping=False)
            try:
                # connect to device
                conn = zk.connect()
                # Get attendances (will return list of Attendance object)
                attendance = conn.get_attendance()
                for entry in attendance:
                    attendance_dict = {
                        'employee_id': format(entry.user_id),
                        'timestamp': format(entry.timestamp),
                        'status': int(format(entry.status)),
                        'punch': int(format(entry.punch)),
                    }
                    attendance_list.append(attendance_dict)
                print('GET Success')
            except Exception as e:
                print(e)
            finally:
                if conn:
                    conn.disconnect()
        return attendance_list


    def create_data(self, data):
        for i in data:
            assignment = self.env['hr.employee.biometric'].search([
                ('device_id', '=', i['employee_id'])
            ])

            if assignment:
                if not self.sudo().search([
                    ('employee_id', '=', assignment.employee_id.id),
                    ('check_in_char', '=', i['check_in']),
                    ('check_out_char', '=', i['check_out']),

                ]):
                    # if self.env['hr.employee'].search([('id', '=', (i['employee_id']))]):
                    self.sudo().create({
                        'employee_id': assignment.employee_id.id,
                        'check_in_char': i['check_in'],
                        'check_out_char': i['check_out'],
                        'state': 'error' if not i['check_out'] else 'draft'
                    })

    def convert_date(self):
        user_tz = self.env.user.tz  # chuoi 'Asia/SaiGon'

        user_tz = pytz.timezone(user_tz)
        for rec in self:
            if rec.state == 'draft':
                if rec.check_in_char:
                    datetime_checkin = datetime.strptime(rec.check_in_char, "%Y-%m-%d %H:%M")
                    datetime_checkin = user_tz.localize(datetime_checkin).astimezone(pytz.utc)
                    datetime_checkin = datetime.strftime(datetime_checkin, "%Y-%m-%d %H:%M")
                    rec.write({
                        'check_in': datetime_checkin,
                    })
                if rec.check_out_char:
                    datetime_checkout = datetime.strptime(rec.check_out_char, "%Y-%m-%d %H:%M")
                    datetime_checkout = user_tz.localize(datetime_checkout).astimezone(pytz.utc)
                    datetime_checkout = datetime.strftime(datetime_checkout, "%Y-%m-%d %H:%M")
                    rec.write({
                        'check_out': datetime_checkout,
                    })

        @api.depends('check_in', 'check_out')
        def _compute_actual_work(self):
            for attendance in self:
                if attendance.check_out and attendance.check_in:
                    delta = attendance.check_out - attendance.check_in
                    attendance.actual_work = delta.total_seconds() / 3600.0
                else:
                    attendance.actual_work = False


        @api.returns('self', lambda value: value.id)
        def copy(self):
            raise exceptions.UserError(_('You cannot duplicate an attendance.'))

    # actual_work = fields.Float(
    #     compute='_compute_actual_work',
    #     store=True, readonly=True
    # )

    # def import_to_attendance(self):
    #     attendance = self.env['hr.attendance']
    #     for rec in self:
    #         if rec.state != 'done' and rec.state != 'error' and rec.check_out and rec.check_in:
    #             attendance_id = None
    #             try:
    #                 attendance_id = attendance.create({
    #                     'employee_id': rec.employee_id.id,
    #                     'check_in': rec.check_in,
    #                     'check_out': rec.check_out
    #                 })
    #             except Exception as e:
    #                 rec.write({
    #                     'state': 'error',
    #                     'error_message': str(e)
    #                 })
    #
    #                 # attendance_id.unlink()
    #                 raise UserError(_(str(e)))
    #             rec.write({
    #                 'state': 'done'
    #             })
    #             self.env.cr.commit()

    # def handle_data(self, data):
    #     result = []
    #     for i in data:
    #         if i['punch'] == 0:
    #             temp = {
    #                 'employee_id': i['employee_id'],
    #                 'check_in': i['timestamp'],
    #                 'check_out': None
    #             }
    #             result.append(temp)
    #         elif i['punch'] == 1:
    #             check = True
    #             for j in result:
    #                 if j['check_out'] is None and j['employee_id'] == i['employee_id'] and j['check_in'].split(' ')[0] == i['timestamp'].split(' ')[0]:
    #                     j['check_out'] = i['timestamp']
    #                     check = False
    #                     break
    #             if check:
    #                 temp = {
    #                     'employee_id': i['employee_id'],
    #                     'check_in': None,
    #                     'check_out': i['timestamp']
    #                 }
    #                 result.append(temp)
    #     return result

    # def create_data(self, data):
    #     drop_all_data = self.sudo().search([])
    #     drop_all_data.unlink()
    #     for i in data:
    #         # assignment = self.env['hr.employee.biometric'].search([
    #         #     ('device_id', '=', i['employee_id'])
    #         # ])
    #         #
    #         # if assignment:
    #             if not self.sudo().search([
    #                 # ('employee_id', '=', assignment.employee_id.id),
    #                 ('employee_id', '=', i['employee_id']),
    #                 ('check_in_char', '=', i['check_in']),
    #                 ('check_out_char', '=', i['check_out']),
    #             ]):
    #                 # if self.env['hr.employee'].search([('id', '=', (assignment.employee_id.id))]):
    #                 if self.env['hr.employee'].search([('id', '=', (i['employee_id']))]):
    #                     self.sudo().create({
    #                         # 'employee_id': assignment.employee_id.id,
    #                         'employee_id': int(i['employee_id']),
    #                         'check_in_char': i['check_in'],
    #                         'check_out_char': i['check_out'],
    #                         'state': 'error' if not i['check_out'] else 'draft'
    #                     })

    # def convert_date(self):
    #     user_tz = self.env.user.tz  # chuoi 'Asia/SaiGon'
    #     user_tz = pytz.timezone(user_tz)
    #     for rec in self:
    #         if rec.state == 'draft':
    #             if rec.check_in_char:
    #                 datetime_checkin = datetime.strptime(rec.check_in_char, "%Y-%m-%d %H:%M:%S")
    #                 datetime_checkin = user_tz.localize(datetime_checkin).astimezone(pytz.utc)
    #                 datetime_checkin = datetime.strftime(datetime_checkin, "%Y-%m-%d %H:%M:%S")
    #                 rec.write({
    #                     'check_in': datetime_checkin,
    #                 })
    #             if rec.check_out_char:
    #                 datetime_checkout = datetime.strptime(rec.check_out_char, "%Y-%m-%d %H:%M:%S")
    #                 datetime_checkout = user_tz.localize(datetime_checkout).astimezone(pytz.utc)
    #                 datetime_checkout = datetime.strftime(datetime_checkout, "%Y-%m-%d %H:%M:%S")
    #                 rec.write({
    #                     'check_out': datetime_checkout,
    #                 })

    @api.depends('check_in', 'check_out')
    def _compute_actual_work(self):
        for attendance in self:
            if attendance.check_out and attendance.check_in:
                delta = attendance.check_out - attendance.check_in
                attendance.actual_work = delta.total_seconds() / 3600.0
            else:
                attendance.actual_work = False
