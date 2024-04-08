# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from inspect import getmembers

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.ssi_decorator import ssi_decorator


class MixinTransactionWinLost(models.AbstractModel):
    _name = "mixin.transaction_win_lost"
    _inherit = [
        "mixin.transaction",
    ]
    _description = "Transaction Mixin - Win & Lost State Mixin"
    _win_state = "win"
    _lost_state = "lost"

    # Attributes related to automatic form view
    _automatically_insert_win_policy_fields = True
    _automatically_insert_win_button = True
    _automatically_insert_win_reason = True
    _automatically_insert_lost_policy_fields = True
    _automatically_insert_lost_button = True
    _automatically_insert_lost_reason = True

    # Attributes related to add element on search view automatically
    _automatically_insert_win_filter = True
    _automatically_insert_lost_filter = True

    # Attributes related to add element on tree view automatically
    _automatically_insert_win_state_badge_decorator = True
    _automatically_insert_lost_state_badge_decorator = True

    lost_reason_id = fields.Many2one(
        string="Lost Reason",
        comodel_name="base.lost_reason",
        readonly=True,
    )

    def _compute_policy(self):
        _super = super(MixinTransactionWinLost, self)
        _super._compute_policy()

    win_ok = fields.Boolean(
        string="Can Mark as Win",
        compute="_compute_policy",
        compute_sudo=True,
    )
    lost_ok = fields.Boolean(
        string="Can Mark as Lost",
        compute="_compute_policy",
        compute_sudo=True,
    )
    real_win_date = fields.Date(
        string="Real Win Date",
        readonly=True,
    )
    real_lost_date = fields.Date(
        string="Real Lost Date",
        readonly=True,
    )
    state = fields.Selection(
        selection_add=[
            ("win", "Win"),
            ("lost", "Lost"),
        ],
        ondelete={
            "win": "set default",
            "lost": "set default",
        },
    )

    def _prepare_win_data(self, real_win_date=False):
        self.ensure_one()
        win_date = real_win_date or fields.Date.today()
        return {
            "state": "win",
            "real_win_date": win_date,
        }

    def _prepare_lost_data(self, real_lost_date=False, lost_reason=False):
        self.ensure_one()
        lost_date = real_lost_date or fields.Date.today()
        return {
            "state": "lost",
            "lost_reason_id": lost_reason and lost_reason.id or False,
            "real_lost_date": lost_date,
        }

    def action_win(self, real_win_date=False):
        for record in self.sudo():
            record._check_win_policy()
            record._run_pre_win_check()
            record._run_pre_win_action()
            record.write(record._prepare_win_data(real_win_date=real_win_date))
            record._run_post_win_check()
            record._run_post_win_action()

    def action_lost(self, real_lost_date=False, lost_reason=False):
        for record in self.sudo():
            record._check_lost_policy()
            record._run_pre_lost_check()
            record._run_pre_lost_action()
            record.write(
                record._prepare_lost_data(
                    real_lost_date=real_lost_date, lost_reason=lost_reason
                )
            )
            record._run_post_lost_check()
            record._run_post_lost_action()

    def _run_pre_win_check(self):
        self.ensure_one()
        cls = type(self)
        methods = []
        for _attr, func in getmembers(cls):
            if self.is_decorator(func, "_pre_win_check"):
                methods.append(func)
        if methods:
            self.run_decorator_method(methods)

    def _run_post_win_check(self):
        self.ensure_one()
        cls = type(self)
        methods = []
        for _attr, func in getmembers(cls):
            if self.is_decorator(func, "_post_win_check"):
                methods.append(func)
        if methods:
            self.run_decorator_method(methods)

    def _run_pre_win_action(self):
        self.ensure_one()
        cls = type(self)
        methods = []
        for _attr, func in getmembers(cls):
            if self.is_decorator(func, "_pre_win_action"):
                methods.append(func)
        if methods:
            self.run_decorator_method(methods)

    def _run_post_win_action(self):
        self.ensure_one()
        cls = type(self)
        methods = []
        for _attr, func in getmembers(cls):
            if self.is_decorator(func, "_post_win_action"):
                methods.append(func)
        if methods:
            self.run_decorator_method(methods)

    def _check_win_policy(self):
        self.ensure_one()
        if self.env.context.get("bypass_win_policy", False):
            return True

        if not self.win_ok:
            error_message = """
            Context: Mark as win %s
            Database ID: %s
            Problem: Document is not allowed to mark as win
            Solution: Check mark as win policy prerequisite
            """ % (
                self._description.lower(),
                self.id,
            )
            raise UserError(_(error_message))

    def _run_pre_lost_check(self):
        self.ensure_one()
        cls = type(self)
        methods = []
        for _attr, func in getmembers(cls):
            if self.is_decorator(func, "_pre_lost_check"):
                methods.append(func)
        if methods:
            self.run_decorator_method(methods)

    def _run_post_lost_check(self):
        self.ensure_one()
        cls = type(self)
        methods = []
        for _attr, func in getmembers(cls):
            if self.is_decorator(func, "_post_lost_check"):
                methods.append(func)
        if methods:
            self.run_decorator_method(methods)

    def _run_pre_lost_action(self):
        self.ensure_one()
        cls = type(self)
        methods = []
        for _attr, func in getmembers(cls):
            if self.is_decorator(func, "_pre_lost_action"):
                methods.append(func)
        if methods:
            self.run_decorator_method(methods)

    def _run_post_lost_action(self):
        self.ensure_one()
        cls = type(self)
        methods = []
        for _attr, func in getmembers(cls):
            if self.is_decorator(func, "_post_lost_action"):
                methods.append(func)
        if methods:
            self.run_decorator_method(methods)

    def _check_lost_policy(self):
        self.ensure_one()
        if self.env.context.get("bypass_lost_policy", False):
            return True

        if not self.lost_ok:
            error_message = """
            Context: Mark as lost %s
            Database ID: %s
            Problem: Document is not allowed to mark as lost
            Solution: Check mark as lost policy prerequisite
            """ % (
                self._description.lower(),
                self.id,
            )
            raise UserError(_(error_message))

    def _prepare_restart_data(self):
        self.ensure_one()
        _super = super(MixinTransactionWinLost, self)
        result = _super._prepare_restart_data()
        result.update(
            {
                "lost_reason_id": False,
            }
        )
        return result

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        result = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        View = self.env["ir.ui.view"]

        view_arch = etree.XML(result["arch"])

        if view_type == "form" and self._automatically_insert_view_element:
            view_arch = self._view_add_win_policy_field(view_arch)
            view_arch = self._view_add_win_button(view_arch)
            view_arch = self._view_add_lost_policy_field(view_arch)
            view_arch = self._view_add_lost_button(view_arch)
            view_arch = self._view_add_lost_reason(view_arch)
            view_arch = self._reorder_header_button(view_arch)
            view_arch = self._reorder_policy_field(view_arch)
        elif view_type == "tree" and self._automatically_insert_view_element:
            view_arch = self._add_win_state_badge_decorator(view_arch)
            view_arch = self._add_lost_state_badge_decorator(view_arch)
        elif view_type == "search" and self._automatically_insert_view_element:
            view_arch = self._add_win_filter_on_search_view(view_arch)
            view_arch = self._add_lost_filter_on_search_view(view_arch)
            view_arch = self._reorder_state_filter_on_search_view(view_arch)

        if view_id and result.get("base_model", self._name) != self._name:
            View = View.with_context(base_model_name=result["base_model"])
        new_arch, new_fields = View.postprocess_and_fields(view_arch, self._name)
        result["arch"] = new_arch
        new_fields.update(result["fields"])
        result["fields"] = new_fields

        return result

    @api.model
    def _add_win_state_badge_decorator(self, view_arch):
        if self._automatically_insert_win_state_badge_decorator:
            _xpath = "/tree/field[@name='state']"
            if len(view_arch.xpath(_xpath)) == 0:
                return view_arch
            node_xpath = view_arch.xpath(_xpath)[0]
            node_xpath.set("decoration-success", "state == 'win'")
        return view_arch

    @api.model
    def _add_lost_state_badge_decorator(self, view_arch):
        if self._automatically_insert_lost_state_badge_decorator:
            _xpath = "/tree/field[@name='state']"
            if len(view_arch.xpath(_xpath)) == 0:
                return view_arch
            node_xpath = view_arch.xpath(_xpath)[0]
            node_xpath.set("decoration-muted", "state == 'lost'")
        return view_arch

    @api.model
    def _add_win_filter_on_search_view(self, view_arch):
        if self._automatically_insert_win_filter:
            view_arch = self._add_view_element(
                view_arch,
                "ssi_transaction_win_lost_mixin.win_filter",
                self._state_filter_xpath,
                "after",
            )
        return view_arch

    @api.model
    def _add_lost_filter_on_search_view(self, view_arch):
        if self._automatically_insert_lost_filter:
            view_arch = self._add_view_element(
                view_arch,
                "ssi_transaction_win_lost_mixin.lost_filter",
                self._state_filter_xpath,
                "after",
            )
        return view_arch

    @api.model
    def _view_add_win_policy_field(self, view_arch):
        if self._automatically_insert_win_policy_fields:
            policy_element_templates = [
                "ssi_transaction_win_lost_mixin.win_policy_field",
            ]
            for template in policy_element_templates:
                view_arch = self._add_view_element(
                    view_arch,
                    template,
                    self._policy_field_xpath,
                    "before",
                )
        return view_arch

    @api.model
    def _view_add_lost_policy_field(self, view_arch):
        if self._automatically_insert_lost_policy_fields:
            policy_element_templates = [
                "ssi_transaction_win_lost_mixin.lost_policy_field",
            ]
            for template in policy_element_templates:
                view_arch = self._add_view_element(
                    view_arch,
                    template,
                    self._policy_field_xpath,
                    "before",
                )
        return view_arch

    @api.model
    def _view_add_win_button(self, view_arch):
        if self._automatically_insert_win_button:
            view_arch = self._add_view_element(
                view_arch,
                "ssi_transaction_win_lost_mixin.button_win",
                "/form/header/field[@name='state']",
                "before",
            )
        return view_arch

    @api.model
    def _view_add_lost_button(self, view_arch):
        if self._automatically_insert_lost_button:
            view_arch = self._add_view_element(
                view_arch,
                "ssi_transaction_win_lost_mixin.button_lost",
                "/form/header/field[@name='state']",
                "before",
            )
        return view_arch

    @api.model
    def _view_add_lost_reason(self, view_arch):
        if self._automatically_insert_lost_reason:
            view_arch = self._add_view_element(
                view_arch,
                "ssi_transaction_win_lost_mixin.lost_reason",
                "/form/sheet/div[@class='oe_left']/div[@class='oe_title']/h1",
                "after",
            )
        return view_arch

    @ssi_decorator.insert_on_tree_view()
    def _01_view_add_tree_lost_button(self, view_arch):
        if self._automatically_insert_lost_button:
            view_arch = self._add_view_element(
                view_arch,
                "ssi_transaction_win_lost_mixin.tree_button_lost",
                "/tree/header",
                "inside",
            )
        return view_arch

    @ssi_decorator.insert_on_tree_view()
    def _01_view_add_tree_win_button(self, view_arch):
        if self._automatically_insert_win_button:
            view_arch = self._add_view_element(
                view_arch,
                "ssi_transaction_win_lost_mixin.tree_button_win",
                "/tree/header",
                "inside",
            )
        return view_arch
