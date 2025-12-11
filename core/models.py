from django.db import models
from django.contrib.auth.models import User


class Household(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200, blank=True)
    join_code = models.CharField(max_length=20, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='households_created')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Membership(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    # Percentage of rent/expenses this member normally pays (0–100)
    share_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        unique_together = ('user', 'household')

    def __str__(self):
        return f"{self.user.username} in {self.household.name}"


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Expense(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='expenses')
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True, blank=True)
    paid_by = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='expenses_paid')
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.amount}"


class ExpenseShare(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='shares')
    member = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='shares')
    share_amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('expense', 'member')

    def __str__(self):
        return f"{self.member.user.username} owes {self.share_amount} for {self.expense.title}"


class Chore(models.Model):
    FREQUENCY_CHOICES = [
        ('once', 'Once'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='chores')
    title = models.CharField(max_length=100)
    assigned_to = models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True, blank=True, related_name='chores')
    due_date = models.DateField()
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='once')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
