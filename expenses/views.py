from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse

from datetime import date
import csv

from .models import Expense, Budget
from .forms import ExpenseForm, RegisterForm, BudgetForm

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Budget.objects.get_or_create(user=user)
            login(request, user)
            return redirect('/')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user)
    search = request.GET.get('search')
    category = request.GET.get('category')
    if search:
        expenses = expenses.filter(title__icontains=search)
    if category:
        expenses = expenses.filter(category=category)
    total_expense = sum(expense.amount for expense in expenses)
    today = date.today()
    monthly_expenses = Expense.objects.filter(
        user=request.user, date__month=today.month, date__year=today.year
    )
    monthly_expense = sum(expense.amount for expense in monthly_expenses)
    budget, created = Budget.objects.get_or_create(user=request.user)
    monthly_budget = budget.monthly_budget
    remaining_budget = monthly_budget - monthly_expense
    total_transactions = expenses.count()
    total_users = User.objects.count()
    total_records = Expense.objects.count()
    recent_expenses = Expense.objects.filter(user=request.user).order_by('-id')[:5]
    categories = {}
    for expense in expenses:
        categories[expense.category] = categories.get(expense.category, 0) + float(expense.amount)
    context = {
        'expenses': expenses,
        'total_expense': total_expense,
        'monthly_budget': monthly_budget,
        'remaining_budget': remaining_budget,
        'monthly_expense': monthly_expense,
        'total_transactions': total_transactions,
        'total_users': total_users,
        'total_records': total_records,
        'recent_expenses': recent_expenses,
        'categories': categories,
    }
    return render(request, 'dashboard.html', context)

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('/')
    else:
        form = ExpenseForm()
    return render(request, 'add_expense.html', {'form': form})

@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'edit_expense.html', {'form': form})

@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    expense.delete()
    return redirect('/')

@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=expenses.csv'
    writer = csv.writer(response)
    writer.writerow(['Title', 'Amount', 'Category', 'Date'])
    expenses = Expense.objects.filter(user=request.user)
    for expense in expenses:
        writer.writerow([expense.title, expense.amount, expense.category, expense.date])
    return response

@login_required
def update_budget(request):
    budget, created = Budget.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = BudgetForm(instance=budget)
    return render(request, 'update_budget.html', {'form': form})
