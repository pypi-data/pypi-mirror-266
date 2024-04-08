# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class BaseSelectCancelReason(models.TransientModel):
    _name = "base.select_cancel_reason"
    _description = "Select Cancel Reason"

    @api.model
    def _default_model_id(self):
        result = False
        model_name = self.env.context.get("active_model", False)
        if model_name:
            obj_model = self.env["ir.model"]
            criteria = [
                ("model", "=", model_name),
            ]
            models = obj_model.search(criteria)
            if len(models) > 0:
                result = models[0]

        return result

    model_id = fields.Many2one(
        string="Model",
        comodel_name="ir.model",
        required=True,
        default=lambda self: self._default_model_id(),
    )
    cancel_reason_ids = fields.Many2many(
        string="Allowed Cancel Reason(s)",
        comodel_name="base.cancel_reason",
        related="model_id.all_cancel_reason_ids",
    )
    cancel_reason_id = fields.Many2one(
        string="Reason",
        comodel_name="base.cancel_reason",
        required=True,
    )

    def action_confirm(self):
        for record in self:
            record._confirm_cancel()

    def _confirm_cancel(self):
        self.ensure_one()
        model_name = self.model_id.model
        obj_record = self.env[model_name]
        record_ids = self.env.context.get("active_ids", [])
        if len(record_ids) > 0:
            records = obj_record.browse(record_ids)
            records.action_cancel(self.cancel_reason_id)
