/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ListController } from "@web/views/list/list_controller";
import { listView } from "@web/views/list/list_view";
// import { useService } from "@web/core/utils/hooks";

class TemporaryButton extends ListController{
    // static template = "button_sale.ListView.Buttons"
    setup(){    
        super.setup();
        this.rpc = this.env.services.rpc;
        this.actionService = this.env.services.action;
    }
    onTestClick(){
        this.actionService.doAction({
            type: 'ir.actions.act_window',
            res_model: 'hr.attendance.temporary',
            name:'Open Wirzard',
            view_mode: 'form',
            view_type: 'form',
            views: [[false,'form']],
            target: 'new',
            res_id: false,
        })

    }
    async _import_data(){
        try {
            let result = await this._call_api();
            if (result){
                await this.rpc("/web/dataset/call_kw",{
                    model: "hr.attendance.temporary",
                    method: "create_data",
                    args: [[], result],
                });
                window.location.reload();
            }
        } catch(error){
            console.error("Error importing data:",error);
        }
    }
    async _call_api(){
        try {
            let result = await this.rpc("/web/dataset/call_kw",{
                model: "hr.attendance.temporary",
                method: "call_api",
                // Array: [{}],
                args: [{}],
            });
            return result;

        } catch(error){
            console.error("Api call failed:",error);
            return null;
        }
    }
}

registry.category("views").add("hr_attendance_temporary_button_tree",{
    ...listView,
    Controller: TemporaryButton,
    buttonTemplate: "button_sale.ListView.Buttons",

});
