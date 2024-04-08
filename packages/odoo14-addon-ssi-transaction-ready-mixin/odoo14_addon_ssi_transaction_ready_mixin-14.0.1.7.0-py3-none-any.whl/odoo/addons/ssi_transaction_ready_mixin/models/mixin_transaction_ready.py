# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from inspect import getmembers

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.ssi_decorator import ssi_decorator


class MixinTransactionReady(models.AbstractModel):
    _name = "mixin.transaction_ready"
    _inherit = [
        "mixin.transaction",
    ]
    _description = "Transaction Mixin - Ready to Start State Mixin"
    _ready_state = "ready"

    # Attributes related to add element on form view automatically
    _automatically_insert_ready_policy_fields = True
    _automatically_insert_ready_button = True

    # Attributes related to add element on search view automatically
    _automatically_insert_ready_filter = True

    # Attributes related to add element on tree view automatically
    _automatically_insert_ready_state_badge_decorator = True

    def _compute_policy(self):
        _super = super(MixinTransactionReady, self)
        _super._compute_policy()

    ready_ok = fields.Boolean(
        string="Can Stagged",
        compute="_compute_policy",
        compute_sudo=True,
    )
    state = fields.Selection(
        selection_add=[
            ("ready", "Ready to Start"),
        ],
        ondelete={
            "ready": "set default",
        },
    )

    def _prepare_ready_data(self):
        self.ensure_one()
        result = {
            "state": self._ready_state,
        }
        if self._create_sequence_state == self._ready_state:
            self._create_sequence()
        return result

    def _run_pre_ready_check(self):
        self.ensure_one()
        cls = type(self)
        methods = []
        for _attr, func in getmembers(cls):
            if self.is_decorator(func, "_pre_ready_check"):
                methods.append(func)
        if methods:
            self.run_decorator_method(methods)

    def _run_post_ready_check(self):
        self.ensure_one()
        cls = type(self)
        methods = []
        for _attr, func in getmembers(cls):
            if self.is_decorator(func, "_post_ready_check"):
                methods.append(func)
        if methods:
            self.run_decorator_method(methods)

    def _run_pre_ready_action(self):
        self.ensure_one()
        cls = type(self)
        methods = []
        for _attr, func in getmembers(cls):
            if self.is_decorator(func, "_pre_ready_action"):
                methods.append(func)
        if methods:
            self.run_decorator_method(methods)

    def _run_post_ready_action(self):
        self.ensure_one()
        cls = type(self)
        methods = []
        for _attr, func in getmembers(cls):
            if self.is_decorator(func, "_post_ready_action"):
                methods.append(func)
        if methods:
            self.run_decorator_method(methods)

    def action_ready(self):
        for record in self.sudo():
            record._check_ready_policy()
            record._run_pre_ready_check()
            record._run_pre_ready_action()
            record.write(record._prepare_ready_data())
            record._run_post_ready_check()
            record._run_post_ready_action()

    def _check_ready_policy(self):
        self.ensure_one()
        if self.env.context.get("bypass_ready_policy", False):
            return True

        if not self.ready_ok:
            error_message = """
            Context: Stage %s
            Database ID: %s
            Problem: Document is not allowed to stage
            Solution: Check stage policy prerequisite
            """ % (
                self._description.lower(),
                self.id,
            )
            raise UserError(_(error_message))

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
            view_arch = self._view_add_ready_policy_field(view_arch)
            view_arch = self._view_add_ready_button(view_arch)
            view_arch = self._reorder_header_button(view_arch)
            view_arch = self._reorder_policy_field(view_arch)
        elif view_type == "tree" and self._automatically_insert_view_element:
            view_arch = self._add_ready_state_badge_decorator(view_arch)
        elif view_type == "search" and self._automatically_insert_view_element:
            view_arch = self._add_ready_filter_on_search_view(view_arch)
            view_arch = self._reorder_state_filter_on_search_view(view_arch)

        if view_id and result.get("base_model", self._name) != self._name:
            View = View.with_context(base_model_name=result["base_model"])
        new_arch, new_fields = View.postprocess_and_fields(view_arch, self._name)
        result["arch"] = new_arch
        new_fields.update(result["fields"])
        result["fields"] = new_fields

        return result

    @api.model
    def _add_ready_state_badge_decorator(self, view_arch):
        if self._automatically_insert_ready_state_badge_decorator:
            _xpath = "/tree/field[@name='state']"
            if len(view_arch.xpath(_xpath)) == 0:
                return view_arch
            node_xpath = view_arch.xpath(_xpath)[0]
            node_xpath.set("decoration-primary", "state == 'ready'")
        return view_arch

    @api.model
    def _add_ready_filter_on_search_view(self, view_arch):
        if self._automatically_insert_ready_filter:
            view_arch = self._add_view_element(
                view_arch,
                "ssi_transaction_ready_mixin.ready_filter",
                self._state_filter_xpath,
                "after",
            )
        return view_arch

    @api.model
    def _view_add_ready_policy_field(self, view_arch):
        if self._automatically_insert_ready_policy_fields:
            policy_element_templates = [
                "ssi_transaction_ready_mixin.ready_policy_field",
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
    def _view_add_ready_button(self, view_arch):
        if self._automatically_insert_ready_button:
            view_arch = self._add_view_element(
                view_arch,
                "ssi_transaction_ready_mixin.button_ready",
                "/form/header/field[@name='state']",
                "before",
            )
        return view_arch

    @ssi_decorator.insert_on_tree_view()
    def _01_view_add_tree_ready_button(self, view_arch):
        if self._automatically_insert_ready_button:
            view_arch = self._add_view_element(
                view_arch,
                "ssi_transaction_ready_mixin.tree_button_ready",
                "/tree/header",
                "inside",
            )
        return view_arch
