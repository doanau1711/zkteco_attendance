# -*- coding: utf-8 -*-
#import datetime
from datetime import datetime, timedelta

import pytz
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime




class ZkAttendance(models.Model):
    _inherit = 'hr.attendance'

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

    status = fields.Selection(
        selection=[
            ('working', 'Working'),
            ('out of work', 'Out of work'),
            ('error', 'Error')
        ],
        default='working',
        help='Employee working status'
    )

    check_in_id = fields.Many2one(
        comodel_name='zk.attendance',
        string='Checkin Log',
    )

    check_out_id = fields.Many2one(
        comodel_name="zk.attendance",
        string="Checkout Log"
    )

    check_in_float = fields.Float(
        store=True,
        compute='_compute_check_in_float_date'
    )

    check_out_float = fields.Float(
        store=True,
        compute='_compute_check_out_float_date'
    )

    check_in_date = fields.Char(
        store=True,
        compute='_compute_check_in_float_date'
    )

    check_out_date = fields.Char(
        store=True,
        compute='_compute_check_out_float_date'
    )

    employee_code = fields.Char(
        compute='_compute_employee_code'
    )

    working_type = fields.Selection([
        ("during", "During"),
        ("overtime", "Overtime")
    ], default="during", string="Working Type")

    first_selfie = fields.Binary(string="First Selfie")
    second_selfie = fields.Binary(string="Second Selfie")
    third_selfie = fields.Binary(string="Third Selfie")
    explain_attendance = fields.Text(string="Explain")

    @api.depends('employee_id')
    def _compute_employee_code(self):
        for rec in self:
            if rec.employee_id:
                model_info = self.env['hr.employee']._fields

                # Check if the field with the given code exists in the model
                if 'code' in model_info:

                    if rec.employee_id.code:
                        rec.employee_code = rec.employee_id.code
                    else:
                        rec.employee_code = ''
                else:
                    rec.employee_code = ''
            else:
                rec.employee_code = ''
    @api.depends('check_in')
    def _compute_check_in_float_date(self):
        for rec in self:
            if rec.check_in:
                check_in = rec.check_in + timedelta(hours=7)
                time_difference = check_in - fields.Datetime.from_string(check_in.date())
                time_as_float = time_difference.total_seconds() / 3600.0  # Convert total seconds to hours
                rec.check_in_float = time_as_float
                rec.check_in_date = check_in.date().strftime('%d/%m/%Y')
            else:
                rec.check_in_date = ''
                rec.check_in_float = 0

    @api.depends('check_out')
    def _compute_check_out_float_date(self):
        for rec in self:
            if rec.check_out:
                check_out = rec.check_out + timedelta(hours=7)
                time_difference = check_out - fields.Datetime.from_string(check_out.date())
                time_as_float = time_difference.total_seconds() / 3600.0  # Convert total seconds to hours
                rec.check_out_float = time_as_float
                rec.check_out_date = check_out.date().strftime('%d/%m/%Y')
            else:
                rec.check_out_date = ''
                rec.check_out_float = 0

    def write(self, vals):
        if vals.get('check_out') and vals.get('status') is None:
            vals.update({
                'status': 'out of work'
            })
        res = super(ZkAttendance, self).write(vals)
        if not self.check_out and self.status != 'working':
            self.write({
                'status': 'working'
            })
        return res

    ## TODO: prevent change status from this
    def resolve_uncheck_out(self):
        if self.check_in:
            
            self.write({
                'status': 'out of work',
                'check_out': self.check_in + relativedelta(hours=8)
            })

