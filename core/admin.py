from django.contrib import admin
from .models import Transaction, Budget

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'txn_type', 'category', 'amount', 'txn_date', 'note')  # use 'user' instead of 'username'
    list_filter = ('txn_type', 'category')
    search_fields = ('user__username', 'category', 'note')  # 'user__username' for related field search

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'month', 'budget_amount')  # use 'user' instead of 'username' and correct amount field
    list_filter = ('month',)
    search_fields = ('user__username', 'month')
