from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('transactions/', views.transactions_page, name='transactions'),
    path('transactions/delete/<int:id>/', views.delete_transaction, name='delete_transaction'),

    path('budget/', views.budget_page, name='budget'),
    path("delete-budget/<int:id>/", views.delete_budget, name="delete_budget"),

    path('export/', views.export_excel, name='export_excel'),
    path('generate-report/', views.generate_pdf_report, name='generate_report'),

    path('logout/', views.logout_user, name='logout'),

]
