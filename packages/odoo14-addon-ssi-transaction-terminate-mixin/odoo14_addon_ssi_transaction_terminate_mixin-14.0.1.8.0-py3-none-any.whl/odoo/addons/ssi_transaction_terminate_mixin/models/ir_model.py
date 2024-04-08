# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class IrModel(models.Model):
    _name = "ir.model"
    _inherit = "ir.model"

    terminate_reason_ids = fields.Many2many(
        string="Terminate Reasons",
        comodel_name="base.terminate_reason",
        relation="rel_model_2_terminate_reason",
        column1="model_id",
        column2="terminate_reason_id",
    )

    def _compute_all_terminate_reason_ids(self):
        obj_reason = self.env["base.terminate_reason"]
        criteria = [
            ("global_use", "=", True),
        ]
        global_reasons = obj_reason.search(criteria)
        for record in self:
            record.all_terminate_reason_ids = (
                global_reasons + record.terminate_reason_ids
            ).ids

    all_terminate_reason_ids = fields.Many2many(
        string="All Terminate Reasons",
        comodel_name="base.terminate_reason",
        compute="_compute_all_terminate_reason_ids",
        store=False,
    )
