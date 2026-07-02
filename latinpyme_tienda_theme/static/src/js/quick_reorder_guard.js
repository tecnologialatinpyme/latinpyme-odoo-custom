/** @odoo-module **/

import websiteSaleUtils from "@website_sale/js/website_sale_utils";

const originalUpdateQuickReorderSidebar = websiteSaleUtils && websiteSaleUtils.updateQuickReorderSidebar;

if (websiteSaleUtils) {
    websiteSaleUtils.updateQuickReorderSidebar = function updateQuickReorderSidebar(data) {
        const quickReorderSidebar = document.querySelector("#quick_reorder_sidebar .offcanvas-body");
        if (!quickReorderSidebar || typeof originalUpdateQuickReorderSidebar !== "function") {
            return;
        }
        return originalUpdateQuickReorderSidebar.call(this, data);
    };
}
