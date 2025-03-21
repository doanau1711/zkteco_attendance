# -*- coding: utf-8 -*-
import datetime
from datetime import datetime, date, timedelta

import logging
from odoo.tools.misc import format_duration

import pytz
from dateutil.relativedelta import relativedelta

from odoo import http
from odoo.http import Response, request

# try:
#     from zk import ZK, const
# except ImportError:
#     _logger.error("Please Install pyzk library.")

_logger = logging.getLogger(__name__)


def float_time_to_hour_minute(value):
    if value < 0:
        return 0, 0
    hours, minutes = divmod(abs(value) * 60, 60)
    minutes = round(minutes)
    if minutes == 60:
        minutes = 0
        hours += 1
    return hours, minutes


class ZKMachineControllers(http.Controller):

    def _response(self):
        return Response('OK', status=200, headers=[('Content-Type', 'text/plain')])

    def _parse_attendance(self, user_tz):
        _logger.info('truoc user_tz')
        # user_tz = pytz.timezone(user_tz)

        data = http.request.httprequest.data.decode('ascii')
        _logger.info('value data')
        vals = (data.replace('\n', '')).split('\t')

        vals[1] = datetime.now()
        # vals[1] = user_tz.localize(vals[1]).astimezone(pytz.utc).replace(tzinfo=None)
        _logger.info('value valls')

        # - relativedelta(hours=7)
        return vals

    @http.route('/iclock/cdata', methods=['GET'], auth='public', type='http', csrf=False)
    def get_iclock_data(self, **kwargs):
        return self._response()

    @http.route('/iclock/cdata', methods=['POST'], auth='public', type='http', csrf=False)
    def post_iclock_data(self, **kwargs):
        _logger.info('------ asd -----')

        try:
            qcontext = http.request.params.copy()
            # _logger.info('******************* post_iclock_data *************: ', qcontext)
            # _logger.info( qcontext)

            # user_tz = self.env.user.tz or 'UTC'
            # local_tz = pytz.timezone(user_tz)
            # now = datetime.now(local_tz)
            print('qcontext: ', qcontext)
            if qcontext.get('table') == 'ATTLOG':
                _logger.info('truoc hr.attendance')
                Attendance = request.env['hr.attendance'].sudo()
                _logger.info('truoc zk.attendance')
                ZKAttendance = request.env['zk.attendance'].sudo()
                _logger.info('truoc hr.biometric.device')
                biometric_id = request.env['hr.biometric.device'].sudo().find_by_serial(qcontext.get('SN') or '')
                _logger.info('truoc vals parse_attendance')
                vals = self._parse_attendance(request.env.user.tz)
                _logger.info(f'Parsed attendance vals: {vals}')
                _logger.info(f'biometric_id: {biometric_id}')
                attendance = ZKAttendance.create({
                    'biometric_device_id': int(biometric_id),
                    'device_id': int(vals[0]),
                    'table': qcontext.get('table') or '',
                    'attendance_type': vals[3],
                    'punch_type': vals[2],
                    'punching_time': vals[1]
                })
                _logger.info(f'Attendance created: {attendance}')

                if attendance:
                    _logger.info('value if attendance')
                    start_float_hour = float(
                        request.env['ir.config_parameter'].sudo().get_param('start_hour_of_day') or 0)
                    _logger.info(f'start float: {start_float_hour}')
                
                    start_hour, start_minute = float_time_to_hour_minute(start_float_hour)
                    _logger.info(f'start hour: {start_hour}, start minute: {start_minute}')
                    
                    user_tz_name = request.env.user.tz or 'UTC'
                    _logger.info(f"User timezone name: {user_tz_name}")

                    try:
                        user_tz = pytz.timezone(user_tz_name)
                        _logger.info(f"User timezone object: {user_tz}")
                    except Exception as e:
                        _logger.warning(f"Invalid timezone '{user_tz_name}', using UTC instead.")
                        user_tz = pytz.timezone('UTC')

                    
                    # _logger.info(start_hour)
                    # user_tz = pytz.timezone(request.env.user.tz)
                    # _logger.info('value usertz',user_tz)

                    # start_time = user_tz.localize(vals[1]).astimezone(pytz.utc).replace(tzinfo=None, hour=start_hour, minute=0, second=0)
                    #
                    # start_time = user_tz.localize(start_time).astimezone(pytz.utc).replace(tzinfo=None)

                    start_time = vals[1].astimezone(user_tz).replace(tzinfo=None).replace(hour=int(start_hour),
                                                                                          minute=int(start_minute),
                                                                                          second=0)
                    _logger.info('vals[1]')
                    _logger.info(vals[1])
                    _logger.info('start_time')
                    _logger.info(start_time)
                    if vals[1].astimezone(user_tz).replace(tzinfo=None) < start_time:
                        start_time -= timedelta(days=1)

                    start_time = user_tz.localize(start_time).astimezone(pytz.utc).replace(tzinfo=None)
                    start_day = start_time
                    _logger.info(start_time)
                    b = Attendance.search([
                        ('employee_id', '=', attendance.employee_id.id),
                        ('check_in', '>', start_day)
                    ], limit=1, order='check_in desc')
                    minimum_time = float(
                        request.env['ir.config_parameter'].sudo().get_param('attendance_minimum_work_time') or 0)
                    

                    if b:  ## not first time check in
                        if b.check_out:  ## already checkout
                            if attendance.employee_id:
                                if (vals[1] - b.check_out).total_seconds() / 3600 > minimum_time:
                                    # _logger.info('trước Attendance create line 104')

                                    Attendance.create({
                                        'employee_id': attendance.employee_id.id,
                                        'attendance_type': vals[3],
                                        'punch_type': vals[2],
                                        'check_in': vals[1],
                                        'check_in_id': attendance.id,
                                        'status': 'working',
                                    })
                        else:  ## dont have checkout
                            # _logger.info('trước if  line 117')
                            # _logger.info((vals[1] - b.check_in).total_seconds() / 3600)

                            if (vals[1] - b.check_in).total_seconds() / 3600 > minimum_time:
                                b.write({
                                    'check_out': vals[1],
                                    'check_out_id': attendance.id,
                                    'status': 'out of work'
                                })
                    else:  ## is first time check in
                        last_check_in = Attendance.search([
                            ('employee_id', '=', attendance.employee_id.id),
                        ], limit=1, order='check_in desc')
                        # _logger.info(last_check_in)
                        if not last_check_in.check_out:  ## check if prevous check in did not check out
                            if last_check_in:
                                last_check_in.write({
                                    'check_out': start_time,
                                    'status': 'error'
                                })
                        if attendance.employee_id:
                            Attendance.create({
                                'employee_id': attendance.employee_id.id,
                                'attendance_type': vals[3],
                                'punch_type': vals[2],
                                'check_in': vals[1],
                                'check_in_id': attendance.id,
                                'status': 'working'
                            })

                _logger.info("++++++++++++Clone Successfull++++++++++++++++++++++")
            return Response('OK', status=200, headers=[('Content-Type', 'text/plain')])
        except Exception as e:
            _logger.debug(str(e))
            return self._response()

    @http.route('/iclock/ping', methods=['GET'], auth='public', type='http', csrf=False)
    def get_iclock_ping(self, **kwargs):
        return Response('OK', status=200, headers=[('Content-Type', 'text/plain')])

    @http.route('/iclock/getrequest', methods=['GET'], auth='public', type='http', csrf=False)
    def get_iclock_getrequest(self, **kwargs):
        return Response('OK', status=200, headers=[('Content-Type', 'text/plain')])
