import datetime
from datetime import datetime,date
import logging
from dateutil.relativedelta import relativedelta
import pytz
from odoo import fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
class ZKAttendance(models.Model):
    _name = 'zk.attendance'
    _description = 'Attendance Logging'

    _rec_name = 'biometric_device_id'

    _sql_constraints = [
        ('attendance_uniq', 'unique (biometric_device_id,device_id,punching_time,punch_type)', 'The attendance ready resolved!')
    ]

    _order = "punching_time DESC"

    biometric_device_id = fields.Many2one(
        comodel_name="hr.biometric.device",
        string='Biometric Device Serial'
    )
    device_id = fields.Integer(string='Biometric Device ID')
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        compute="_compute_employee_id",
        depends=['biometric_device_id', 'device_id'],
        store=True
    )

    def _compute_employee_id(self):
        for rec in self:
            rec.employee_id = None
            if rec.biometric_device_id and rec.device_id:
                res = self.env['hr.employee.biometric'].sudo() \
                    .search([('biometric_device_id', '=', rec.biometric_device_id.id), ('device_id', '=', rec.device_id)])
                if res:
                    rec.employee_id = res.employee_id

    table = fields.Char(string='Biometric Action')

    punching_time = fields.Datetime(string='Punching Time', help="Give the punching time")
    punch_type = fields.Selection(
        selection=[
            ('0', 'Check In'),
            ('1', 'Check Out'),
            ('2', 'Break Out'),
            ('3', 'Break In'),
            ('4', 'Overtime In'),
            ('5', 'Overtime Out')
        ],
        string='Punching Type'
    )

    attendance_type = fields.Selection(
        selection=[
            ('0', 'Odoo'),
            ('1', 'Finger'),
            ('15', 'Face'),
            ('2', 'Type_2'),
            ('3', 'Password'),
            ('4', 'Card')
        ],
        default='0',
        string='Category',
        help="Select the attendance type"
    )

    def time_now(self):
        Attendance = self.env['hr.attendance'].sudo()

       

        if self.punch_type == '0':  # checkin
            b=Attendance.search([
            ('employee_id', '=', self.employee_id.id),
            ('check_out', '=', None)
            ], limit=1, order='check_in desc')
            if b:
                if b.check_in >= datetime.combine(date.today(), datetime.min.time()):
                    return   # ready checked in
            a = Attendance.search([
                            ('employee_id', '=', self.employee_id.id)
                        ], order='check_in desc', limit=1)
            if a:            
                if not a.check_out:
                    
                    a.resolve_uncheck_out()

            Attendance.create({
                'employee_id': self.employee_id.id,
                'attendance_type': self.attendance_type,
                'punch_type': self.punch_type,
                'check_in': self.punching_time,
                'check_in_id': self.id
            })

        elif self.punch_type == '1':  # checkout:
            attended = Attendance.search([('employee_id', '=', self.employee_id.id)],
                                         limit=1, order='check_in desc')
            if not attended.check_out:
                diff_tms = self.punching_time - attended.check_in
                punching_time = attended.check_in + relativedelta(
                    seconds=100) if diff_tms.total_seconds() < 60 else self.punching_time
                attended.write({
                    'check_out': punching_time,
                    'check_out_id': self.id
                })


