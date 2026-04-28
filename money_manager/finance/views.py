from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Income, Expense
from django.db.models import Sum

# --- AUTHENTICATION ---
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! Please login.")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm

def login_view(request):
    # 🛑 PROPER VALIDATION: If user is already logged in, send them to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

# --- DASHBOARD ---
@login_required
def dashboard(request):
    income_total = Income.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    expense_total = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    context = {
        'total_income': income_total,
        'total_expense': expense_total,
        'balance': income_total - expense_total,
    }
    return render(request, 'dashboard.html', context)

# --- INCOME CRUD ---
@login_required
def income_page(request):
    if request.method == 'POST':
        source = request.POST.get('source')
        amount = request.POST.get('amount')
        Income.objects.create(user=request.user, source=source, amount=amount)
        messages.success(request, "Income added successfully.")
        return redirect('income')
    
    incomes = Income.objects.filter(user=request.user).order_by('-date')
    return render(request, 'income.html', {'incomes': incomes})

@login_required
def delete_income(request, id):
    income = get_object_or_404(Income, id=id, user=request.user)
    income.delete()
    messages.info(request, "Income record deleted.")
    return redirect('income')

# --- EXPENSE CRUD ---
@login_required
def expense_page(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        amount = request.POST.get('amount')
        Expense.objects.create(user=request.user, category=category, amount=amount)
        messages.success(request, "Expense recorded successfully.")
        return redirect('expense')
    
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    return render(request, 'expense.html', {'expenses': expenses})

@login_required
def delete_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    expense.delete()
    messages.info(request, "Expense record deleted.")
    return redirect('expense')






from django.utils import timezone
from datetime import datetime, timedelta

def report_view(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    incomes = Income.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)

    if start_date and end_date:
        # Convert strings to actual Python date objects
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Add 1 day to the end_date so we capture the full final day
        # (Filter becomes: Everything BEFORE the start of the next day)
        next_day = end_dt + timedelta(days=1)

        incomes = incomes.filter(date__gte=start_dt, date__lt=next_day)
        expenses = expenses.filter(date__gte=start_dt, date__lt=next_day)
 
    
    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'incomes': incomes,
        'expenses': expenses,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'report.html', context)







import openpyxl
from django.http import HttpResponse
from .models import Income, Expense # Ensure your models are imported

def export_excel(request):
    # 1. Create a workbook and a sheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Financial Statement"

    # 2. Define the header row
    headers = ['Date', 'Type', 'Category/Source', 'Amount (₹)']
    ws.append(headers)

    # 3. Get the data (you can also apply date filters here like your report view)
    incomes = Income.objects.filter(user=request.user).order_by('-date')
    expenses = Expense.objects.filter(user=request.user).order_by('-date')

    # 4. Add Income data to rows
    for obj in incomes:
        ws.append([obj.date.strftime('%Y-%m-%d'), 'Income', obj.source, obj.amount])

    # 5. Add Expense data to rows
    for obj in expenses:
        ws.append([obj.date.strftime('%Y-%m-%d'), 'Expense', obj.category, obj.amount])

    # 6. Prepare the response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename=FinTrack_Statement.xlsx'
    
    wb.save(response)
    return response