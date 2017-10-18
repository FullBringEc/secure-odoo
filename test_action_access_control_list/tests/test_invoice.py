# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl).

from odoo.addons.action_access_control_list.controllers.main import \
    SecuredEnvironment
from odoo.exceptions import AccessError
from odoo.tests import SavepointCase


class TestInvoice(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestInvoice, cls).setUpClass()

        cls.test_user = cls.env.ref('base.user_demo')

        cls.env['ir.protected.action'].search([]).unlink()

        cls.protected_action = cls.env['ir.protected.action'].create({
            'name': 'invoice_validate',
            'technical_name': 'action_invoice_open',
            'model_id': cls.env['account.invoice'],
        })

        cls.journal = cls.env['account.journal'].search(
            [('type', '=', 'sale')], limit=1)
        cls.account = cls.env['account.account'].search(
            [('user_type_id.type', '=', 'receivable')], limit=1)
        cls.account_income = cls.env['account.account'].search(
            [('user_type_id.type', '=', 'other')], limit=1)

        cls.partner = cls.env['res.partner'].create({'name': 'Customer'})

        cls.out_invoice = cls.env['account.invoice'].create({
            'account_id': cls.account.id,
            'partner_id': cls.partner.id,
            'journal_id': cls.journal.id,
            'type': 'out_invoice',
        })

        cls.account_invoice_line_1 = cls.env['account.invoice.line'].create({
            'invoice_id': cls.out_invoice.id,
            'name': 'Line 1',
            'account_id': cls.account_income.id,
            'price_unit': 20,
        })

        cls.env['ir.model.access'].search(
            [('group_id.users', '=', cls.test_user.id)]).unlink()

        cls.action = cls.env['ir.protected.action'].create({
            'name': 'Validate Invoices',
            'technical_name': 'action_invoice_open',
            'model_id': cls.env.ref('account.model_account_invoice').id,
        })

    def test_01_invoice_validate(self):
        env = SecuredEnvironment(self.env.cr, self.test_user.id, {})
        inv = env['account.invoice'].browse(self.out_invoice.id)
        inv.action_invoice_open()
        self.assertTrue(inv.move_id)

    def test_02_invoice_validate_not_secured(self):
        inv = self.out_invoice.sudo(self.test_user)
        with self.assertRaises(AccessError):
            inv.action_invoice_open()

    def _add_action_access(self, domain=None):
        self.env['ir.action.access'].create({
            'action_id': self.action.id,
            'group_id': self.test_user.groups_id[0].id,
            'model_id': self.env.ref('account.model_account_invoice').id,
            'domain': domain,
        })

    def test_10_check_access_success(self):
        self._add_action_access()
        action = self.action.sudo(self.test_user)
        action.check_access(self.out_invoice.id)

    def test_11_check_access_no_access(self):
        action = self.action.sudo(self.test_user)
        with self.assertRaises(AccessError):
            action.check_access([self.out_invoice.id])

    def test_12_check_access_with_domain(self):
        self._add_action_access("[('type', '=', 'out_invoice')]")
        action = self.action.sudo(self.test_user)
        action.check_access([self.out_invoice.id])

    def test_13_check_access_wrong_domain(self):
        self._add_action_access("[('type', '=', 'in_invoice')]")
        action = self.action.sudo(self.test_user)
        with self.assertRaises(AccessError):
            action.check_access([self.out_invoice.id])

    def test_14_check_access_both_domain(self):
        self._add_action_access("[('type', '=', 'out_invoice')]")
        self._add_action_access("[('type', '=', 'in_invoice')]")
        action = self.action.sudo(self.test_user)
        action.check_access([self.out_invoice.id])

    def _add_read_access(self):
        self.env['ir.model.access'].create({
            'name': 'Invoice Access',
            'groups_id': self.test_user.groups_id[0].id,
            'model_id': self.env.ref('account.model_account_invoice').id,
            'perm_read': 1,
            'perm_write': 0,
            'perm_create': 0,
            'perm_unlink': 0,
        })

    def test_20_invoice_read(self):
        self.out_invoice.action_invoice_open()
        self._add_read_access()
        env = SecuredEnvironment(self.env.cr, self.test_user.id, {})
        env._bypass_exception = 'account.invoice'
        inv = env['account.invoice'].browse(self.out_invoice.id)
        inv.read(fields=['outstanding_credits_debits_widget'])

    def test_21_invoice_read_not_secured(self):
        self.out_invoice.action_invoice_open()
        self._add_read_access()
        inv = self.out_invoice.sudo(self.test_user)
        with self.assertRaises(AccessError):
            inv.read(fields=['outstanding_credits_debits_widget'])

    def test_22_invoice_read_no_access(self):
        self.out_invoice.action_invoice_open()
        env = SecuredEnvironment(self.env.cr, self.test_user.id, {})
        env._bypass_exception = 'account.invoice'
        inv = env['account.invoice'].browse(self.out_invoice.id)
        with self.assertRaises(AccessError):
            inv.read(fields=['outstanding_credits_debits_widget'])