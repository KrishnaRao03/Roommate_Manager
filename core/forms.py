from django import forms
from .models import Household, Expense, Chore, Membership


class HouseholdForm(forms.ModelForm):
    class Meta:
        model = Household
        fields = ["name", "address", "join_code"]


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        # household and paid_by are set in the view
        fields = ["title", "amount", "category", "date"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }


class ChoreForm(forms.ModelForm):
    """Chore form, household is passed in from the view to limit choices."""

    class Meta:
        model = Chore
        # assigned_to is a Membership
        fields = ["title", "assigned_to", "due_date", "frequency", "status"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        household = kwargs.pop("household", None)
        super().__init__(*args, **kwargs)

        # Limit assigned_to to memberships for this household
        if household is not None:
            self.fields["assigned_to"].queryset = Membership.objects.filter(
                household=household
            )

from django import forms
from django.contrib.auth.models import User


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Enter password"})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm password"})
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "First name", "class": "form-control"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last name", "class": "form-control"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email address", "class": "form-control"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data["email"].lower()
        user.username = email
        user.email = email
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
class AddMemberForm(forms.Form):
    email = forms.EmailField(
        label="Member email",
        widget=forms.EmailInput(attrs={
            "placeholder": "friend@example.com",
            "class": "form-control"
        })
    )
    share_percentage = forms.DecimalField(
        label="Share percentage",
        min_value=0,
        max_value=100,
        decimal_places=2,
        initial=0,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "step": "0.01"
        })
    )
