from decimal import Decimal
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from account.models import Account


class InsufficientBalance(Exception):
    pass

class NegativeOrZeroAmount(Exception):
    pass


class Transfer(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    from_account = models.ForeignKey(Account, models.CASCADE, related_name='transfers_in')
    to_account = models.ForeignKey(Account, models.CASCADE, related_name='transfers_out')
    amount = models.DecimalField(max_digits=18, decimal_places=2)

    @staticmethod
    def do_transfer(from_account: Account, to_account: Account, amount: Decimal):
        if amount <= 0:
            raise NegativeOrZeroAmount()

        from_account.refresh_from_db()
        to_account.refresh_from_db()

        if from_account.balance < amount:
            raise InsufficientBalance()

        from_account.balance -= amount
        to_account.balance += amount

        from_account.save()
        to_account.save()

        return Transfer.objects.create(
            from_account=from_account,
            to_account=to_account,
            amount=amount
        )


class ScheduledPayment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    pay_day = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(28)])
    from_account = models.ForeignKey(Account, models.CASCADE, related_name='sch_transfers_in')
    to_account = models.ForeignKey(Account, models.CASCADE, related_name='sch_transfers_out')
    amount = models.DecimalField(max_digits=18, decimal_places=2)

    @staticmethod
    def create_scheduled_payment(from_account: Account, to_account: Account, amount: Decimal, pay_day: int):
        if amount <= 0:
            raise NegativeOrZeroAmount()

        return ScheduledPayment.objects.create(
            from_account=from_account,
            to_account=to_account,
            amount=amount,
            pay_day=pay_day
        )

    def do_transfer(self):
        return Transfer.do_transfer(self.from_account, self.to_account, self.amount)


# class OtherActivities(models.Model):
#     created_at = models.DateTimeField(auto_now_add=True)
#     account = models.ForeignKey(Account, models.CASCADE, related_name='other_transfers')
#     type_of_operation = models.CharField #deposit, withdraw, send, recieve
#     amount = models.DecimalField(max_digits=18, decimal_places=2)
#
#     @staticmethod
#     def do_transfer(account: Account, type_of_operation: str, amount: Decimal):
#         # operation logic here
#
#         return OtherActivities.objects.create(
#             account=account,
#             type_of_operation=type_of_operation,
#             amount=amount
#         )
