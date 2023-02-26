from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def get_worker_rate(self):
        if not self.env['ir.default'].get("res.config.settings", "worker_rate"):
            self.env['ir.default'].set("res.config.settings", "worker_rate", 1)
        return self.env['ir.default'].get("res.config.settings", "worker_rate")

    worker_rate = fields.Float(default=get_worker_rate, string="Worker Float")

    @api.onchange('worker_rate')
    def set_worker_rate(self):
        self.env['ir.default'].set("res.config.settings", "worker_rate", self.worker_rate)

    @api.model
    def set_default_rate(self):
        self.env['ir.default'].set("res.config.settings", "worker_rate", 1.0)
