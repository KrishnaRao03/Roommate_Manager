from .forms import RegisterForm
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Sum
from django.shortcuts import redirect

from .models import Household, Membership, Expense, Chore, ExpenseShare
from .forms import HouseholdForm, ExpenseForm, ChoreForm


def home_redirect(request):
    """If user is logged in go to dashboard, else go to login page."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


@login_required
def dashboard(request):
    """Simple dashboard: show households where this user is a member."""
    memberships = Membership.objects.filter(user=request.user)
    households = [m.household for m in memberships]

    context = {
        'households': households,
    }
    # IMPORTANT: template name is EXACTLY 'core/dashboard.html'
    return render(request, 'core/dashboard.html', context)


@login_required
def household_detail(request, pk):
    """Show one household with its expenses, chores, and balances, plus the current
    user's own share and tasks."""
    household = get_object_or_404(Household, pk=pk)

    # Ensure user is a member of this household
    current_membership = get_object_or_404(Membership, user=request.user, household=household)

    expenses = Expense.objects.filter(household=household).order_by('-date')
    chores = Chore.objects.filter(household=household).order_by('due_date')

    # Balance calculation: how much each member paid vs owes
    memberships = Membership.objects.filter(household=household).select_related('user')
    balances = []
    for m in memberships:
        paid_total = Expense.objects.filter(
            household=household, paid_by=m
        ).aggregate(total=Sum('amount'))['total'] or 0

        share_total = ExpenseShare.objects.filter(
            expense__household=household, member=m
        ).aggregate(total=Sum('share_amount'))['total'] or 0

        balances.append({
            'membership': m,
            'paid_total': paid_total,
            'share_total': share_total,
            'balance': paid_total - share_total,  # positive = others owe them
        })

    # Current user's own summary
    my_paid_total = next((b['paid_total'] for b in balances if b['membership'] == current_membership), 0)
    my_share_total = next((b['share_total'] for b in balances if b['membership'] == current_membership), 0)
    my_balance = my_paid_total - my_share_total

    my_chores_assigned = chores.filter(assigned_to=current_membership)
    my_chores_pending = my_chores_assigned.filter(status='pending')
    my_chores_completed = my_chores_assigned.filter(status='completed')

    context = {
        'household': household,
        'expenses': expenses,
        'chores': chores,
        'balances': balances,
        'current_membership': current_membership,
        'my_paid_total': my_paid_total,
        'my_share_total': my_share_total,
        'my_balance': my_balance,
        'my_chores_pending': my_chores_pending,
        'my_chores_completed': my_chores_completed,
    }
    return render(request, 'core/household_detail.html', context)


@login_required
def add_member(request, pk):
    """Add an existing user to this household by email."""
    household = get_object_or_404(Household, pk=pk)
    membership = get_object_or_404(Membership, user=request.user, household=household)

    # Only admins can add members
    if membership.role != 'admin':
        messages.error(request, "Only admins can add members.")
        return redirect('household_detail', pk=pk)

    from .forms import AddMemberForm
    if request.method == 'POST':
        form = AddMemberForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower()
            share_percentage = form.cleaned_data['share_percentage']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "No user with that email has registered yet.")
                return redirect('add_member', pk=pk)

            # Prevent duplicates
            if Membership.objects.filter(user=user, household=household).exists():
                messages.info(request, "That user is already a member of this household.")
                return redirect('household_detail', pk=pk)

            Membership.objects.create(
                user=user,
                household=household,
                role='member',
                share_percentage=share_percentage
            )
            messages.success(request, "Member added successfully.")
            return redirect('household_detail', pk=pk)
    else:
        form = AddMemberForm()

    return render(request, 'core/add_member.html', {
        'household': household,
        'form': form,
    })


@login_required
def household_create(request):
    """Create a new household and make current user the admin member."""
    if request.method == 'POST':
        form = HouseholdForm(request.POST)
        if form.is_valid():
            household = form.save(commit=False)
            household.created_by = request.user
            household.save()

            # Create membership as admin
            Membership.objects.create(
                user=request.user,
                household=household,
                role='admin',
                share_percentage=0
            )

            return redirect('household_detail', pk=household.pk)
    else:
        form = HouseholdForm()

    return render(request, 'core/household_form.html', {'form': form})


@login_required
def expense_create(request, household_pk):
    """Create a new expense for a household and split cost equally."""
    household = get_object_or_404(Household, pk=household_pk)
    membership = get_object_or_404(Membership, user=request.user, household=household)

    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.household = household
            expense.paid_by = membership
            expense.save()

            # Split equally among all members
            members = Membership.objects.filter(household=household)
            count = members.count()
            if count > 0:
                per_head = expense.amount / count
                for m in members:
                    ExpenseShare.objects.create(
                        expense=expense,
                        member=m,
                        share_amount=per_head
                    )

            return redirect('household_detail', pk=household.pk)
    else:
        form = ExpenseForm()

    return render(request, 'core/expense_form.html', {
        'form': form,
        'household': household,
    })


@login_required
def chore_create(request, household_pk):
    """Create a new chore for a household."""
    household = get_object_or_404(Household, pk=household_pk)
    Membership.objects.get(user=request.user, household=household)

    if request.method == 'POST':
        form = ChoreForm(request.POST, household=household)
        if form.is_valid():
            chore = form.save(commit=False)
            chore.household = household
            chore.save()
            return redirect('household_detail', pk=household.pk)
    else:
        form = ChoreForm(household=household)

    return render(request, 'core/chore_form.html', {
        'form': form,
        'household': household,
    })


@login_required
def chore_toggle_status(request, pk):
    """Mark a chore as completed / pending."""
    chore = get_object_or_404(Chore, pk=pk)
    # Only members of the household may do this
    Membership.objects.get(user=request.user, household=chore.household)

    if chore.status == 'pending':
        chore.status = 'completed'
    else:
        chore.status = 'pending'
    chore.save()

    return redirect('household_detail', pk=chore.household.pk)


@login_required
def logout_view(request):
    """Log out and go back to login page."""
    logout(request)
    return redirect('login')



@login_required
def profile_redirect(request):
    """Handle /accounts/profile/ by sending the user to the dashboard."""
    return redirect('dashboard')

def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully. Welcome!")
            return redirect("dashboard")
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})


def email_login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        email = request.POST.get("email", "").lower()
        password = request.POST.get("password", "")

        User = get_user_model()
        user = None

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "registration/login.html")
