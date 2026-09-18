import { patch } from "@web/core/utils/patch";
import { redirect } from "@web/core/utils/urls";
import { CartService } from "@website_sale/js/cart_service";

const SIGNUP_URL = "/web/signup?redirect=/shop";
const SIGNUP_ERROR =
    "odoo.addons.website_sale_hide_public_price.controllers.cart.SignupRequired";

patch(CartService.prototype, {
    async add(...args) {
        try {
            const { signup_required } = await this.rpc("/shop/cart/authentication", {});
            if (signup_required) {
                redirect(SIGNUP_URL);
                return 0;
            }
            // Authenticate before configurators, price notifications or cart writes.
            return await super.add(...args);
        } catch (error) {
            // The session may expire while a product configurator is open.
            if (error.data?.name === SIGNUP_ERROR) {
                redirect(SIGNUP_URL);
                return 0;
            }
            throw error;
        }
    },
});
