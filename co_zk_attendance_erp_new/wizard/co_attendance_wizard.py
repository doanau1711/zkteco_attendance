from odoo import fields, models, api, _


class CoAttendance(models.TransientModel):
    _name = "co.hr.attendance.wizard"
    _description = "HR Attendance Wizard"

    working_type = fields.Selection([
        ("during", "During"),
        ("overtime", "Overtime")
    ], default="during", string="Working Type")

    first_selfie = fields.Binary(string="First Selfie")
    second_selfie = fields.Binary(string="Second Selfie")
    third_selfie = fields.Binary(string="Third Selfie")
    explain_attendance = fields.Text(string="Explain")

    def submit_checkin(self):
        action = self._context.get("action")
        attendance_action = action.get("attendance")

        hr_attendance = self.env["hr.attendance"].sudo().search([("id", "=", attendance_action.get("id"))])

        hr_attendance.write({
            "working_type": self.working_type,
            "explain_attendance": self.explain_attendance,
            "first_selfie": self.first_selfie or False,
            "second_selfie": self.second_selfie or False,
            "third_selfie": self.third_selfie or False
        })

        return action
