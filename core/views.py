from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Transaction, Budget
import pandas as pd
from django.http import HttpResponse


# ---------------- LOGIN ----------------
def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "core/login.html")


# ---------------- REGISTER ----------------
def register_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        if password != confirm:
            messages.error(request, "Passwords do not match")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
        else:
            User.objects.create_user(username=username, password=password)
            messages.success(request, "Account created successfully!")
            return redirect("login")

    return render(request, "core/register.html")


# ---------------- DASHBOARD ----------------
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "core/dashboard.html")


# ---------------- TRANSACTIONS ----------------
def transactions_page(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.method == "POST":
        Transaction.objects.create(
            user=request.user,
            txn_type=request.POST.get("type"),
            category=request.POST.get("category"),
            amount=request.POST.get("amount"),
            txn_date=request.POST.get("date"),
            note=request.POST.get("note")
        )
        messages.success(request, "Transaction added!")

    records = Transaction.objects.filter(user=request.user)
    return render(request, "core/transactions.html", {"records": records})


def delete_transaction(request, id):
    Transaction.objects.get(id=id).delete()
    messages.success(request, "Transaction deleted")
    return redirect("transactions")


# ---------------- BUDGET ----------------
def budget_page(request):
    if request.method == "POST":
        Budget.objects.create(
            user=request.user,
            month=request.POST.get("month"),
            budget_amount=request.POST.get("amount")
        )
        messages.success(request, "Budget saved")

    return render(request, "core/budget.html")


# ---------------- EXPORT TO EXCEL ----------------
def export_excel(request):
    records = Transaction.objects.filter(user=request.user).values()
    df = pd.DataFrame(records)

    file_path = "FinTrak_Report.xlsx"
    df.to_excel(file_path, index=False)

    with open(file_path, "rb") as f:
        response = HttpResponse(f.read(), content_type="application/ms-excel")
        response["Content-Disposition"] = "attachment; filename=FinTrak_Report.xlsx"
        return response


# ---------------- LOGOUT ----------------
def logout_user(request):
    logout(request)
    return redirect("login")
