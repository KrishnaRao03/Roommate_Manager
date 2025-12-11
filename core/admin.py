from django.contrib import admin
from .models import Household, Membership, ExpenseCategory, Expense, ExpenseShare, Chore


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')
    search_fields = ('name',)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'household', 'role', 'share_percentage')
    list_filter = ('role', 'household')


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'household', 'amount', 'paid_by', 'date')
    list_filter = ('household', 'category')
    search_fields = ('title',)


@admin.register(ExpenseShare)
class ExpenseShareAdmin(admin.ModelAdmin):
    list_display = ('expense', 'member', 'share_amount')


@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    list_display = ('title', 'household', 'assigned_to', 'due_date', 'status')
    list_filter = ('household', 'status', 'frequency')
    