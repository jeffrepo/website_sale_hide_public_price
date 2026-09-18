from unittest.mock import patch

from odoo.tests import tagged
from odoo.tests.common import new_test_user
from odoo.addons.website_sale.controllers.cart import Cart
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.tests.common import MockRequest, WebsiteSaleCommon

from ..controllers.cart import (
    PublicPriceCart, PublicPriceWebsiteSale, SIGNUP_URL, SignupRequired,
)


@tagged('post_install', '-at_install')
class TestCartAccess(WebsiteSaleCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.controller = PublicPriceCart()
        cls.checkout_controller = PublicPriceWebsiteSale()
        cls.portal_user = new_test_user(
            cls.env, login='public_price_portal', groups='base.group_portal',
        )

    def test_public_cannot_create_cart(self):
        website = self.website.with_user(self.public_user)
        before = self.env['sale.order'].search_count([])
        with MockRequest(website.env, website=website) as req:
            with self.assertRaises(SignupRequired):
                self.controller.add_to_cart(
                    product_template_id=self.product.product_tmpl_id.id,
                    product_id=self.product.id, quantity=2,
                )
            self.assertFalse(req.session.get('sale_order_id'))
        self.assertEqual(self.env['sale.order'].search_count([]), before)

    def test_public_cannot_change_existing_cart(self):
        website = self.website.with_user(self.public_user)
        lines_before = self.cart.order_line.read(['product_uom_qty'])
        with MockRequest(website.env, website=website, sale_order_id=self.cart.id):
            with self.assertRaises(SignupRequired):
                self.controller.update_cart(self.cart.order_line[0].id, 99)
            with self.assertRaises(SignupRequired):
                self.controller.clear_cart()
            with self.assertRaises(SignupRequired):
                self.controller.add_to_cart(
                    self.product.product_tmpl_id.id, self.product.id,
                )
            self.assertEqual(self.controller.cart_quantity(), 0)
        self.assertEqual(self.cart.order_line.read(['product_uom_qty']), lines_before)

    def test_public_cart_and_checkout_redirect_without_reading_prices(self):
        website = self.website.with_user(self.public_user)
        with MockRequest(website.env, website=website) as req:
            with patch.object(req, 'redirect') as redirect:
                with patch.object(Cart, 'cart') as parent_cart:
                    self.controller.cart()
                    redirect.assert_called_once_with(SIGNUP_URL)
                    parent_cart.assert_not_called()
                redirect.reset_mock()
                with patch.object(WebsiteSale, '_check_cart') as parent_check:
                    self.checkout_controller._check_cart(self.cart)
                    redirect.assert_called_once_with(SIGNUP_URL)
                    parent_check.assert_not_called()

    def test_authentication_checks_current_user(self):
        for user in (self.public_user, self.portal_user, self.env.user):
            with self.subTest(user=user.login):
                website = self.website.with_user(user)
                with MockRequest(website.env, website=website):
                    self.assertEqual(
                        self.controller.cart_authentication(),
                        {'signup_required': user == self.public_user},
                    )

    def test_authenticated_users_keep_parent_behavior(self):
        for user in (self.portal_user, self.env.user):
            website = self.website.with_user(user)
            with self.subTest(user=user.login), MockRequest(website.env, website=website):
                for method, args, kwargs in (
                    ('add_to_cart', (self.product.product_tmpl_id.id, self.product.id),
                     {'quantity': 3, 'linked_products': []}),
                    ('update_cart', (12, 3), {'product_id': self.product.id}),
                    ('clear_cart', (), {}),
                    ('cart_quantity', (), {}),
                    ('cart', (), {'revive_method': 'merge'}),
                ):
                    expected = object()
                    with patch.object(Cart, method, return_value=expected) as parent:
                        self.assertIs(getattr(self.controller, method)(*args, **kwargs), expected)
                        parent.assert_called_once_with(*args, **kwargs)
                with patch.object(WebsiteSale, '_check_cart', return_value=None) as parent:
                    self.assertIsNone(self.checkout_controller._check_cart(self.cart))
                    parent.assert_called_once_with(self.cart)

    def test_portal_user_can_add_product_after_login(self):
        website = self.website.with_user(self.portal_user)
        with MockRequest(website.env, website=website) as req:
            self.assertFalse(req.cart)
            # Authentication itself must never add the previously attempted product.
            self.assertEqual(self.controller.cart_authentication(), {'signup_required': False})
            self.assertFalse(req.cart)
            result = self.controller.add_to_cart(
                product_template_id=self.product.product_tmpl_id.id,
                product_id=self.product.id, quantity=2,
            )
            self.assertEqual(result['quantity'], 2)
            self.assertEqual(req.cart.order_line.product_id, self.product)
            self.assertEqual(req.cart.order_line.product_uom_qty, 2)
