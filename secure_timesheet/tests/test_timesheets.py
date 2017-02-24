# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import fields
from openerp.exceptions import ValidationError
from openerp.addons.secure_account.tests import common


class TestTimesheets(common.TestAccountBase):

    @classmethod
    def setUpClass(cls):
        super(TestTimesheets, cls).setUpClass()

        cls.user = cls.env['res.users'].create({
            'name': 'User 1',
            'login': 'timesheet_user',
            'email': 'root@localhost',
            'groups_id': [(4, cls.env.ref('base.group_user').id)],
        })

        cls.product = cls.env['product.product'].create({
            'name': 'My Product',
            'type': 'service',
        })

        cls.employee = cls.env['hr.employee'].create({
            'name': 'My Employee',
            'user_id': cls.user.id,
            'journal_id': cls.analytic_journal.id,
        })

        now = datetime.now()
        cls.date_from = fields.Date.to_string(now)
        cls.sheet = cls.env['hr_timesheet_sheet.sheet'].create({
            'employee_id': cls.employee.id,
            'date_from': cls.date_from,
            'date_to': now + relativedelta(weeks=1, days=-1),
        })

        cls.timesheet = cls.env['hr.analytic.timesheet'].create({
            'name': '/',
            'user_id': cls.user.id,
            'date': now,
            'amount': -100,
            'unit_amount': 5,
            'product_id': cls.product.id,
            'journal_id': cls.analytic_journal.id,
            'account_id': cls.analytic_acc_1.id,
            'general_account_id': cls.account_1.id,
        })

        cls.sheet.refresh()

    def test_01_delete_timesheet_line_draft(self):
        self.assertEqual(len(self.sheet.timesheet_ids), 1)
        self.timesheet.unlink()
        self.assertEqual(len(self.sheet.timesheet_ids), 0)

    def test_02_delete_timesheet_line_confirmed(self):
        self.sheet.button_confirm()
        self.assertEqual(len(self.sheet.timesheet_ids), 1)
        with self.assertRaises(ValidationError):
            self.timesheet.unlink()

    def test_03_write_timesheet_line_draft(self):
        self.assertEqual(len(self.sheet.timesheet_ids), 1)
        self.assertEqual(self.timesheet.amount, -100)
        self.timesheet.amount = -200
        self.assertEqual(self.timesheet.amount, -200)

    def test_04_write_timesheet_line_confirmed(self):
        self.sheet.button_confirm()
        self.assertEqual(len(self.sheet.timesheet_ids), 1)
        with self.assertRaises(ValidationError):
            self.timesheet.amount = -200

    def test_05_delete_analytic_line_confirmed(self):
        self.sheet.button_confirm()
        self.assertEqual(len(self.sheet.timesheet_ids), 1)
        with self.assertRaises(ValidationError):
            self.timesheet.line_id.unlink()

    def test_06_write_analytic_line_draft(self):
        self.assertEqual(len(self.sheet.timesheet_ids), 1)
        self.assertEqual(self.timesheet.amount, -100)
        self.timesheet.line_id.amount = -200
        self.assertEqual(self.timesheet.amount, -200)

    def test_07_write_analytic_line_confirmed(self):
        self.sheet.button_confirm()
        self.assertEqual(len(self.sheet.timesheet_ids), 1)
        with self.assertRaises(ValidationError):
            self.timesheet.line_id.amount = -200

    def test_08_write_sheet_draft(self):
        now = datetime.now()
        new_date = fields.Date.to_string(now + relativedelta(days=1))
        self.assertEqual(self.sheet.date_from, self.date_from)
        self.sheet.date_from = new_date
        self.assertEqual(self.sheet.date_from, new_date)

    def test_09_write_sheet_confirmed(self):
        self.sheet.button_confirm()
        now = datetime.now()
        new_date = fields.Date.to_string(now + relativedelta(days=1))
        self.assertEqual(self.sheet.date_from, self.date_from)
        with self.assertRaises(ValidationError):
            self.sheet.date_from = new_date