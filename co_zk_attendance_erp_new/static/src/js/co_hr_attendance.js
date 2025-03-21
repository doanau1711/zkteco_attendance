/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class MyCustomAttendances extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.actionService = useService("action");
        this.state = useState({
            employee: null,
            hours_today: null,
        });

        onMounted(() => this.loadEmployeeData());
    }

    async loadEmployeeData() {
        const userId = odoo.session_info.user_id;
        const employees = await this.rpc("/web/dataset/call_kw/hr.employee/search_read", {
            model: "hr.employee",
            method: "search_read",
            args: [[["user_id", "=", userId]], ["attendance_state", "name", "hours_today"]],
        });

        if (employees.length > 0) {
            this.state.employee = employees[0];
            this.state.hours_today = employees[0].hours_today;
        }
    }

    async updateAttendance() {
        if (!this.state.employee) return;

        const result = await this.rpc("/web/dataset/call_kw/hr.employee/attendance_manual", {
            model: "hr.employee",
            method: "attendance_manual",
            args: [[this.state.employee.id], "hr_attendance.hr_attendance_action_my_attendances"],
        });

        if (result.action && this.state.employee.attendance_state === "checked_in") {
            this.actionService.doAction(result.action);
        } else if (result.action && this.state.employee.attendance_state === "checked_out") {
            this.openSignOutWizard(result.action);
        } else if (result.warning) {
            this.actionService.doWarn(result.warning);
        }
    }

    openSignOutWizard(action) {
        this.actionService.doAction({
            name: "Explain Attendance",
            type: "ir.actions.act_window",
            res_model: "co.hr.attendance.wizard",
            view_mode: "form",
            views: [[false, "form"]],
            target: "new",
            res_id: false,
            context: { action },
        });
    }
}

registry.category("actions").add("my_custom_hr_attendance", MyCustomAttendances);
