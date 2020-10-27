from django.test import TestCase

from account.models import Account
from customer.models import Customer
from transfer.models import Transfer, NegativeOrZeroAmount, ScheduledPayment, InsufficientBalance


class TransferTest(TestCase):
    def setUp(self):
        super(TransferTest, self).setUp()

        customer = Customer.objects.create(
            email='test@test.invalid',
            full_name='Test Customer',
        )

        self.account1 = Account.objects.create(number=123, owner=customer, balance=1000)
        self.account2 = Account.objects.create(number=456, owner=customer, balance=1000)

    def test_basic_transfer(self):
        Transfer.do_transfer(self.account1, self.account2, 100)

        self.assertEqual(self.account1.balance, 900)
        self.assertEqual(self.account2.balance, 1100)
        self.assertTrue(Transfer.objects.filter(
            from_account=self.account1,
            to_account=self.account2,
            amount=100,
        ).exists())

    def test_zero_or_negative_amount_for_transfer(self):
        with self.assertRaises(NegativeOrZeroAmount):
            Transfer.do_transfer(self.account1, self.account2, 0)

        with self.assertRaises(NegativeOrZeroAmount):
            Transfer.do_transfer(self.account1, self.account2, -10)

    def test_basic_scheduled_payment(self):
        for day in range(1, 28, 2):
            ScheduledPayment.create_scheduled_payment(self.account1, self.account2, 10, day)

        self.assertEqual(ScheduledPayment.objects.all().count(), 14)

        self.assertTrue(ScheduledPayment.objects.filter(
            from_account=self.account1,
            to_account=self.account2,
            amount=10,
            pay_day=1
        ).exists())

        tmp = ScheduledPayment.objects.get(from_account=self.account1, to_account=self.account2, amount=10, pay_day=1)
        tmp.do_transfer()
        self.assertTrue(Transfer.objects.filter(
            from_account=self.account1,
            to_account=self.account2,
            amount=10,
        ).exists())

        self.account1.refresh_from_db()
        self.account2.refresh_from_db()

        self.assertEqual(self.account1.balance, 990)
        self.assertEqual(self.account2.balance, 1010)


    def test_lost_all_money_through_scheduled_payment(self):
        tmp = ScheduledPayment.create_scheduled_payment(self.account1, self.account2, 110, 1)
        with self.assertRaises(InsufficientBalance):
            for i in range(10):
                tmp.do_transfer()


    def test_scheduled_payment_zero_or_negative_amount(self):
        with self.assertRaises(NegativeOrZeroAmount):
            ScheduledPayment.create_scheduled_payment(self.account1, self.account2, 0, 1)

        with self.assertRaises(NegativeOrZeroAmount):
            ScheduledPayment.create_scheduled_payment(self.account1, self.account2, -10, 1)




