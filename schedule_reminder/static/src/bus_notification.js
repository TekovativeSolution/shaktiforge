/** @odoo-module **/

import { simpleNotificationService } from "@bus/simple_notification_service";
import { patch } from "@web/core/utils/patch";
import { markup } from "@odoo/owl";

patch(simpleNotificationService, {
    start(env, { bus_service, notification: notificationService }) {
        bus_service.subscribe("simple_notification", ({ message, sticky, title, type }) => {
            // Show normal Odoo notification
            notificationService.add(markup(message), { sticky, title, type });

            // Play a sound when notification comes
            const audio = new Audio('/schedule_reminder/static/sounds/new-notification.mp3'); // you can use your own sound file
            audio.play().catch(err => {
                console.warn("Audio play failed:", err);
            });
        });
        bus_service.start();
    },
});