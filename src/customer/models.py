from django.db import models


class Customer(models.Model):
    email = models.EmailField()
    full_name = models.CharField(max_length=200)
    default_account = models.ForeignKey(
        'account.Account',
        on_delete=models.SET_NULL,
        null=True,
        default=None
    )
