/** @odoo-module **/

import { registry } from "@web/core/registry";

// Unregister the existing `odooAccountItem` if it's registered in the item registry
registry.category('user_menuitems').remove('odoo_account');
registry.category('user_menuitems').remove('separator');
registry.category('user_menuitems').remove('documentation');
registry.category('user_menuitems').remove('support');


// Optionally, you can redefine it if you need to change its behavior instead of completely removing it.
// If you want to do nothing, you can leave this part commented out or empty.
// registry.category('items').add('odooAccountItem', {
//     type: "item",
//     id: "account",
//     description: _t("Custom Odoo.com account"),
//     callback: () => {
//         // Define new behavior here if needed.
//     },
//     sequence: 60,
// });
