from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('transactions/', views.transactions_page, name='transactions'),
    path('transactions/delete/<int:id>/', views.delete_transaction, name='delete_transaction'),
    path('budget/', views.budget_page, name='budget'),
    path('export/', views.export_excel, name='export_excel'),
    path('logout/', views.logout_user, name='logout'),
]
