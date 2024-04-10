# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class BaseLostReason(models.Model):
    _name = "base.lost_reason"
    _description = "Lost Reason"

    name = fields.Char(
        string="Lost Reason",
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
