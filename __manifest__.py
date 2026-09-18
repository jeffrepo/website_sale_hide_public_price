{
    'name': 'Website Sale Hide Public Prices',
    'summary': 'Hide public prices and require sign-in before adding products to the cart',
    'version': '19.0.1.1.0',
    'category': 'Website/eCommerce',
    'author': 'Silva technologies',
    'license': 'LGPL-3',
    'depends': ['website_sale', 'auth_signup'],
    'data': [
        'views/website_sale_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_sale_hide_public_price/static/src/js/cart_service.js',
        ],
        'web.assets_unit_tests': [
            'website_sale_hide_public_price/static/tests/cart_service.test.js',
        ],
        'web.assets_unit_tests_setup': [
            'website_sale/static/src/js/cart_service.js',
            'website_sale_hide_public_price/static/src/js/cart_service.js',
        ],
    },
    'installable': True,
    'application': False,
}
