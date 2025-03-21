from datetime import timedelta

import pytz

from odoo import fields, models, api

def float_time_to_hour_minute(value):
    if value < 0:
        return 0, 0
    hours, minutes = divmod(abs(value) * 60, 60)
    minutes = round(minutes)
    if minutes == 60:
        minutes = 0
        hours += 1
    return hours, minutes

class CoHrAttendanceZk(models.Model):
    _name = 'co.hr.attendance.zk'


    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        required=True
    )

    time_stamp = fields.Datetime(
        required=True
    )


    def import_to_attendance(self):
        sorted_records = sorted(self, key=lambda record: record.time_stamp)
        Attendance = self.env['hr.attendance']
        for rec in sorted_records:
            start_float_hour = float(
                self.env['ir.config_parameter'].sudo().get_param('start_hour_of_day') or 0)
            start_hour, start_minute = float_time_to_hour_minute(start_float_hour)

            user_tz = pytz.timezone(self.env.user.tz)


            start_time = rec.time_stamp.astimezone(user_tz).replace(tzinfo=None).replace(hour=int(start_hour),
                                                                                  minute=int(start_minute),
                                                                                  second=0)

            if rec.time_stamp.astimezone(user_tz).replace(tzinfo=None) < start_time:
                start_time -= timedelta(days=1)

            start_time = user_tz.localize(start_time).astimezone(pytz.utc).replace(tzinfo=None)
            start_day = start_time
            b = Attendance.search([
                ('employee_id', '=', rec.employee_id.id),
                ('check_in', '>', start_day)
            ], limit=1, order='check_in desc')
            minimum_time = float(
                self.env['ir.config_parameter'].sudo().get_param('attendance_minimum_work_time') or 0)


            if b:  ## not first time check in
                if b.check_out:  ## already checkout
                    if rec.employee_id:
                        if (rec.time_stamp - b.check_out).total_seconds() / 3600 > minimum_time:
                            # _logger.info('trước Attendance create line 104')

                            Attendance.create({
                                'employee_id': rec.employee_id.id,
                                'attendance_type': '1',
                                'check_in': rec.time,
                                'status': 'working',
                            })
                else:  ## dont have checkout

                    if (rec.time_stamp - b.check_in).total_seconds() / 3600 > minimum_time:
                        b.write({
                            'check_out': rec.time_stamp,
                            'status': 'out of work'
                        })
            else:  ## is first time check in
                last_check_in = Attendance.search([
                    ('employee_id', '=', rec.employee_id.id),
                ], limit=1, order='check_in desc')
                if not last_check_in.check_out:  ## check if prevous check in did not check out
                    if last_check_in:
                        last_check_in.write({
                            'check_out': start_time,
                            'status': 'error'
                        })
                if rec.employee_id:
                    Attendance.create({
                        'employee_id': rec.employee_id.id,
                        'attendance_type': '1',
                        'check_in': rec.time_stamp,
                        'status': 'working'
                    })
