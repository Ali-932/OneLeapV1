from django.db import models
from django.db.models import Sum
from djmoney.models.fields import MoneyField
from treenode.models import TreeNodeModel


class TransactionTypeChoices(models.TextChoices):
    invoice = 'invoice', 'Invoice'
    income = 'income', 'Income'
    expense = 'expense', 'Expense'
    bill = 'bill', 'Bill'


class AccountTypeChoices(models.TextChoices):
    ASSETS = 'ASSETS', 'Assets'
    LIABILITIES = 'LIABILITIES', 'Liabilities'
    INCOME = 'INCOME', 'Income'
    EXPENSES = 'EXPENSES', 'Expenses'
    EQUITY = 'EQUITY', 'Equity',
    NET_EARNINGS = 'NET_EARNINGS', 'Net Earnings'


class JournalEntryTypeChoices(models.TextChoices):
    OE = 'OPENING ENTRY', 'Opening Entry'
    TE = 'TRANSFER ENTRY', 'Transfer Entry'
    CE = 'CLOSING ENTRY', 'Closing Entry'
    AE = 'ADJUSTMENT ENTRY', 'Adjustment Entry'
    COE = 'Compound Entry', 'Compound Entry'
    RE = 'REVERSAL ENTRY', 'Reversal Entry'


class Account(TreeNodeModel):
    name = models.CharField('Name', max_length=255)
    code = models.IntegerField(unique=True)
    type = models.CharField('Type', max_length=255, choices=AccountTypeChoices.choices, null=True, blank=True)
    frozen = models.BooleanField(default=False)
    statement = models.CharField('statement', max_length=255, null=True, blank=True)
    # balance = MoneyField(max_digits=14, decimal_places=2, default_currency='USD', default=0)
    treenode_display_field = "name"

    def __str__(self):
        return self.name

    def get_balance(self):
        node_children_including_self = [*self.get_children_queryset(), self]
        ac = Account.objects.filter(id__in=[i.id for i in node_children_including_self])
        return ac.values('account_JE__amount_currency').annotate(sum=Sum('account_JE__amount')).order_by()


class Transaction(models.Model):
    type = models.CharField('Type', max_length=255, choices=TransactionTypeChoices.choices, null=True)
    description = models.CharField('Description', max_length=255, null=True, blank=True)
    date = models.DateField('Date', auto_now_add=True, null=True, blank=True)


class JournalEntry(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, related_name="account_JE")
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True, related_query_name="transaction_JE")
    amount = MoneyField(max_digits=19, decimal_places=2, null=True)
    date = models.DateField('Date', auto_now_add=True, null=True)
    type = models.CharField('Type', max_length=255, choices=JournalEntryTypeChoices.choices, null=True, blank=True)
    notes = models.CharField('Notes', max_length=255, null=True, blank=True)
    reference_number = models.CharField('Reference', max_length=255, null=True, blank=True)

    # reference number that states the source of the information

    class Meta:
        verbose_name_plural = 'Journal Entries'

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     if self.account.balance.default_currency != self.amount.default_currency:
    #         raise ValueError('Currency mismatch')
    #     self.account.balance += self.amount
    #     self.account.save()
