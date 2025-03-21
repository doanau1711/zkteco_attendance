from odoo import fields, models, api


class EmployeeBiometric(models.Model):
    _name = 'hr.employee.biometric'
    _description = 'Biometric Device'

    _sql_constraints = [
        ('employee_biometric_device_uniq', 'unique (employee_id,biometric_device_id)', 'The device has been setting up for employee!'),
        ('biometric_device_uniq', 'unique (biometric_device_id,device_id)', 'The device id has been setting up for biometric!')
    ]
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    biometric_device_id = fields.Many2one('hr.biometric.device', 'Biometric Device Id', required=True)
    device_id = fields.Integer('Device Id', required=True)

    @api.model
    def create(self, vals):
        res = super(EmployeeBiometric, self).create(vals)
        zk_attendance = self.env['zk.attendance']
        if res.device_id:
            zk_attendance.search([
                ('device_id', '=', res.device_id)
            ]).employee_id = res.employee_id
        return res