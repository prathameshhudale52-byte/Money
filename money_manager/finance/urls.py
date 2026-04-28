from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Core
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Income
    path('income/', views.income_page, name='income'),
    path('income/delete/<int:id>/', views.delete_income, name='delete_income'),
    
    # Expense
    path('expense/', views.expense_page, name='expense'),
    path('expense/delete/<int:id>/', views.delete_expense, name='delete_expense'),



    path('report/', views.report_view, name='report'),
    path('export-excel/', views.export_excel, name='export_excel'),
]