from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Transaction, Budget
import pandas as pd
from django.http import HttpResponse

from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.contrib.auth.decorators import login_required
import calendar

# Expense grouping for chart
from django.db.models import Sum
from datetime import datetime
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from django.conf import settings
import os

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

    # Last 5 transactions
    transactions = Transaction.objects.filter(user=request.user).order_by('-id')[:5]

    # EXPENSE grouped by category
    expense_data = (
        Transaction.objects
        .filter(user=request.user, txn_type="Expense")
        .values("category")
        .annotate(total=Sum("amount"))
        .order_by("category")
    )

    # INCOME grouped by category
    income_data = (
        Transaction.objects
        .filter(user=request.user, txn_type="Income")
        .values("category")
        .annotate(total=Sum("amount"))
        .order_by("category")
    )

    # Total expenses
    total_expense = (
        Transaction.objects
        .filter(user=request.user, txn_type="Expense")
        .aggregate(total=Sum("amount"))["total"] or 0
    )

    # Total income
    total_income = (
        Transaction.objects
        .filter(user=request.user, txn_type="Income")
        .aggregate(total=Sum("amount"))["total"] or 0
    )

    # Budgets
    budgets = Budget.objects.filter(user=request.user).order_by("month")

    # Monthly expenses for budget comparison (optional, can be used later)
    monthly_expense_data = (
        Transaction.objects
        .filter(user=request.user, txn_type="Expense")
        .values("txn_date__month")
        .annotate(total=Sum("amount"))
        .order_by("txn_date__month")
    )

    context = {
        "transactions": transactions,
        "expense_data": expense_data,
        "income_data": income_data,
        "budgets": budgets,
        "total_expense": total_expense,
        "total_income": total_income,
        "monthly_expense_data": monthly_expense_data,
    }

    return render(request, "core/dashboard.html", context)



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
    # Save budget
    if request.method == "POST":
        Budget.objects.create(
            user=request.user,
            month=request.POST.get("month"),
            budget_amount=request.POST.get("amount")  # Make sure field name matches your model
        )
        messages.success(request, "Budget saved")

    # Fetch all budgets of the logged-in user
    budgets = Budget.objects.filter(user=request.user).order_by('-id')

    return render(request, "core/budget.html", {"budgets": budgets})

def delete_budget(request, id):
    budget = Budget.objects.get(id=id, user=request.user)
    budget.delete()
    messages.success(request, "Budget deleted successfully.")
    return redirect("budget")


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


def generate_pdf_report(request):
    if not request.user.is_authenticated:
        return redirect("login")
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Budget_Report.pdf"'

    pdf = canvas.Canvas(response, pagesize=A4)
    # Set PDF metadata title
    pdf.setTitle(f"Budget Report - {request.user.username}")
    width, height = A4
    margin = 50
    y = height - margin

    # ===== Report date top-right =====
    pdf.setFont("Helvetica", 10)
    # report_date = datetime.now().strftime("%d %B %Y")
    report_datetime = datetime.now().strftime("%d %B %Y, %I:%M %p")
    pdf.drawRightString(width - margin, y + 10, f"Report Date: {report_datetime}")

    # ===== Logo centered =====
    logo_path = os.path.join(settings.BASE_DIR, 'fintrak', 'static', 'core', 'images', 'logo.png')
    logo_width = 120
    logo_height = 60
    if os.path.exists(logo_path):
        pdf.drawImage(logo_path, (width - logo_width)/2, y - logo_height, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')
    y -= logo_height + 20

    # ===== Report title centered =====
    pdf.setFont("Helvetica-Bold", 16)
    report_title = "Budget Report"
    pdf.drawCentredString(width / 2, y, f"{report_title} - {request.user.username}")
    y -= 30

    # ===== Fetch budgets =====
    budgets = Budget.objects.filter(user=request.user).order_by("month")

    for b in budgets:
        # Parse month/year
        try:
            year_number = int(b.month.split("-")[0])
            month_number = int(b.month.split("-")[1])
        except:
            year_number = datetime.now().year
            month_number = datetime.now().month

        month_name = calendar.month_name[month_number]

        # ===== Month heading and budget in same line =====
        pdf.setFont("Helvetica-Bold", 16)
        pdf.setFillColor(colors.HexColor("#2E86C1"))
        month_budget_text = f"{month_name} {year_number}  |  Budget: {b.budget_amount}"
        pdf.drawCentredString(width/2, y, month_budget_text)
        y -= 25

        # Fetch expenses
        expenses = Transaction.objects.filter(
            user=request.user,
            txn_type="Expense",
            txn_date__year=year_number,
            txn_date__month=month_number
        )

        # Table data
        table_data = [["Date", "Category", "Amount"]]
        total_expense = 0
        for e in expenses:
            table_data.append([e.txn_date.strftime("%d-%b-%Y"), e.category, e.amount])
            total_expense += e.amount

        if len(table_data) == 1:
            table_data.append(["-", "No expenses recorded", "-"])

        # Remaining balance
        remaining = b.budget_amount - total_expense
        table_data.append(["", "Total Expenses", total_expense])
        table_data.append(["", "Remaining Budget", remaining])

        # Table styling
        table = Table(table_data, colWidths=[150, 200, 150])
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3498db")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 1), (-1, -3), colors.whitesmoke),
            ('BACKGROUND', (0, -2), (-1, -2), colors.HexColor("#f9e79f")),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#d5f5e3")),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
        ])
        table.setStyle(style)

        # Draw table
        w, h = table.wrapOn(pdf, width - 2*margin, y)
        if y - h < 50:
            pdf.showPage()
            y = height - margin
            # Redraw logo on new page
            if os.path.exists(logo_path):
                pdf.drawImage(logo_path, (width - logo_width)/2, y - logo_height, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')
            # Redraw report date
            pdf.setFont("Helvetica", 10)
            pdf.drawRightString(width - margin, y + 10, f"Report Date: {report_datetime}")
            y -= logo_height + 20
        table.drawOn(pdf, (width - w)/2, y - h)
        y -= h + 30

        if y < 100:
            pdf.showPage()
            y = height - margin

    pdf.save()
    return response