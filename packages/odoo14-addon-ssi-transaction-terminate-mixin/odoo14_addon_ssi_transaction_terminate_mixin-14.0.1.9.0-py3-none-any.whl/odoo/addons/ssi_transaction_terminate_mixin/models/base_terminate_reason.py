# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class BaseTerminateReason(models.Model):
    _name = "base.terminate_reason"
    _description = "Terminate Reason"

    name = fields.Char(
        string="Terminate Reason",
        required=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    note = fields.Text(
        string="Note",
    )
    global_use = fields.Boolean(
        string="Global Use",
        default=False,
    )
