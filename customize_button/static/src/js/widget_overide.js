/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ActionService } from "@web/webclient/actions/action_service";

class PhoneCallAction {
    setup() {
        const phoneNumber = this.props?.context?.phone_number;
        if (phoneNumber) {
            window.location.href = `tel:${phoneNumber}`;
        }
    }
}

registry.category("actions").add("call_phone", PhoneCallAction);
