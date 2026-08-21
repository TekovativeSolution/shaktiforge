/** @odoo-module **/

import { simpleNotificationService } from "@bus/simple_notification_service";
import { patch } from "@web/core/utils/patch";
import { markup } from "@odoo/owl";

patch(simpleNotificationService,{
    start(env, { bus_service, notification: notificationService }) {
        bus_service.subscribe("simple_notification", ({ message, sticky, title, type, sound_file }) => {
            if (sound_file) {
                const audio = new Audio(sound_file);
                audio.play().catch(e => console.error("Error playing sound:", e));
            }
            notificationService.add(markup(message), { sticky, title, type });
        });
        bus_service.start();
    },
})