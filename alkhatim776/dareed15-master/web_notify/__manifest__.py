# pylint: disable=missing-docstring
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Web Notify",
    "summary": """
        Send notification messages to user""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV," "AdaptiveCity," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/web",
    "depends": ["web", "bus", "base"],
    "data": [],
    "assets": {
        "web.assets_backend": [
           #("prepend","/web/static/src/scss/webclient.scss"),
           ("prepend","/web_notify/static/src/scss/webclient.scss"),
           ("prepend","/web_notify/static/src/js/web_client.js"),
           ("prepend","/web_notify/static/src/js/widgets/notification.js"),
        ],
    },
    "demo": ["views/res_users_demo.xml"],
    "installable": True,
}
