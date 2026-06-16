from django import forms
from .models import Expense, Budget
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            'title',
            'amount',
            'category',
            'date',
            'description'
        ]

class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2'
        ]

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['monthly_budget']

        widgets = {
            'monthly_budget': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter Monthly Budget'
                }
            )
        }
