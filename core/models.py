from django.db import models
from django.contrib import messages
from django.db import models
from django.contrib.auth.models import User


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    txn_type = models.CharField(max_length=20)
    category = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    txn_date = models.DateField()
    note = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.category}"


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.CharField(max_length=20)
    budget_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.month



