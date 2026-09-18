from odoo import _
from odoo.exceptions import UserError
from odoo.http import request, route

from odoo.addons.website_sale.controllers.cart import Cart
from odoo.addons.website_sale.controllers.main import WebsiteSale


SIGNUP_URL = '/web/signup?redirect=/shop'


class SignupRequired(UserError):
    """Signal a missing session without returning cart contents or prices."""


def _require_cart_user():
    if request.env.user._is_public():
        raise SignupRequired(_("Create an account or sign in before using the cart."))


class PublicPriceCart(Cart):

    @route(
        '/shop/cart/authentication', type='jsonrpc', auth='public',
        methods=['POST'], website=True, readonly=True,
    )
    def cart_authentication(self):
        # Check the live session, including pages left open before login/logout.
        return {'signup_required': request.env.user._is_public()}

    @route()
    def cart(self, *args, **kwargs):
        if request.env.user._is_public():
            return request.redirect(SIGNUP_URL)
        return super().cart(*args, **kwargs)

    @route()
    def add_to_cart(self, *args, **kwargs):
        # Run before the parent can create a sale order or any order lines.
        _require_cart_user()
        return super().add_to_cart(*args, **kwargs)

    @route()
    def update_cart(self, *args, **kwargs):
        _require_cart_user()
        return super().update_cart(*args, **kwargs)

    @route()
    def clear_cart(self, *args, **kwargs):
        _require_cart_user()
        return super().clear_cart(*args, **kwargs)

    @route()
    def cart_quantity(self):
        if request.env.user._is_public():
            return 0
        return super().cart_quantity()


class PublicPriceWebsiteSale(WebsiteSale):

    def _check_cart(self, order_sudo):
        # Also protect checkout URLs for anonymous sessions with an older cart.
        if request.env.user._is_public():
            return request.redirect(SIGNUP_URL)
        return super()._check_cart(order_sudo)
