import { describe, expect, test } from "@odoo/hoot";
import { browser } from "@web/core/browser/browser";
import { patchWithCleanup } from "@web/../tests/web_test_helpers";
import { CartService } from "@website_sale/js/cart_service";
import "@website_sale_hide_public_price/js/cart_service";

describe.current.tags("headless");

function makeService(rpc) {
    const service = Object.create(CartService.prototype);
    service.rpc = rpc;
    patchWithCleanup(browser, {
        location: {
            origin: "https://shop.example.com",
            pathname: "/shop",
            assign: (url) => expect.step(new URL(url).pathname + new URL(url).search),
        },
    });
    service._makeRequest = () => {
        expect.step("add-product");
        return 2;
    };
    service._openProductConfigurator = () => {
        throw new Error("An anonymous visitor must not open a configurator");
    };
    return service;
}

for (const [label, product, options] of [
    ["product page", { productTemplateId: 1, productId: 2 }, {}],
    ["buy now", { productTemplateId: 1, productId: 2 }, { isBuyNow: true }],
    ["dynamic variant", { productTemplateId: 1, ptavs: [3] }, {}],
    ["combo", { productTemplateId: 1, isCombo: true }, {}],
]) {
    test(`public ${label} redirects without creating a cart or loading prices`, async () => {
        const service = makeService(async (route) => {
            expect(route).toBe("/shop/cart/authentication");
            expect.step("authenticate");
            return { signup_required: true };
        });
        expect(await service.add(product, options)).toBe(0);
        expect.verifySteps(["authenticate", "/web/signup?redirect=/shop"]);
    });
}

test("authenticated customers can add the product normally", async () => {
    const service = makeService(async (route) => {
        expect.step(route);
        return route === "/shop/cart/authentication" ? { signup_required: false } : false;
    });
    expect(await service.add({ productTemplateId: 1, productId: 2, quantity: 2 })).toBe(2);
    expect.verifySteps([
        "/shop/cart/authentication", "/website_sale/should_show_product_configurator",
        "add-product",
    ]);
});

test("expiration after the session check redirects without reporting success", async () => {
    const service = makeService(async () => ({ signup_required: false }));
    service._makeRequest = async () => {
        const error = new Error("Session expired");
        error.data = {
            name: "odoo.addons.website_sale_hide_public_price.controllers.cart.SignupRequired",
        };
        throw error;
    };
    expect(await service.add({ productId: 2 }, { isBuyNow: true })).toBe(0);
    expect.verifySteps(["/web/signup?redirect=/shop"]);
});

test("unrelated errors are preserved", async () => {
    const service = makeService(async () => {
        throw new Error("Connection lost");
    });
    await expect(service.add({ productId: 2 })).rejects.toThrow("Connection lost");
    expect.verifySteps([]);
});
