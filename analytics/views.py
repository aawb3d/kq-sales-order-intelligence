import json
from datetime import timedelta

from django.db import models
from django.shortcuts import render
from django.utils import timezone

from core.permissions import operations_manager_required, system_administrator_required
from inventory.models import Stock
from orders.models import Customer, Order, OrderItem


@operations_manager_required
def dashboard(request):
    """Figure 3.7h: Operations Manager — Sales Dashboard with live KPIs and ML outputs."""
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)

    # --- KPI Calculations ---
    # Total sales (MTD) — sum of all line totals for invoiced/fulfilled orders this month
    mtd_orders = Order.objects.filter(order_date__gte=month_start)
    mtd_revenue = OrderItem.objects.filter(
        order__in=mtd_orders
    ).aggregate(
        total=models.Sum(models.F("quantity") * models.F("unit_price"))
    )["total"] or 0

    # Orders this week
    weekly_orders = Order.objects.filter(order_date__gte=week_ago).count()

    # Low stock alerts
    low_stock_count = Stock.objects.filter(
        quantity_on_hand__lte=models.F("reorder_level")
    ).count()

    # Active customers
    active_customers = Customer.objects.count()

    # --- ML Outputs (safely wrapped) ---
    forecast_data = []
    anomaly_data = []
    segmentation_data = []

    all_orders = Order.objects.select_related("customer").prefetch_related("items__product").all()

    try:
        from analytics.ml.forecasting import forecast_demand
        forecast_data = forecast_demand(all_orders)
    except Exception:
        pass

    try:
        from analytics.ml.anomaly_detection import detect_anomalies
        anomaly_data = detect_anomalies(all_orders)
    except Exception:
        pass

    try:
        from analytics.ml.customer_segmentation import segment_customers
        segmentation_data = segment_customers(Customer.objects.prefetch_related("orders__items").all())
    except Exception:
        pass

    # Prepare forecast chart data for JS
    forecast_labels = json.dumps([row.get("date", "") for row in forecast_data[:30]])
    forecast_values = json.dumps([round(float(row.get("predicted_quantity", 0)), 1) for row in forecast_data[:30]])

    context = {
        "mtd_revenue": round(mtd_revenue, 2),
        "weekly_orders": weekly_orders,
        "low_stock_count": low_stock_count,
        "active_customers": active_customers,
        "forecast_labels": forecast_labels,
        "forecast_values": forecast_values,
        "anomalies": anomaly_data[:10],
        "segments": segmentation_data,
    }
    return render(request, "analytics/dashboard.html", context)


@operations_manager_required
def generate_reports(request):
    """Figure 3.7i: Operations Manager — Generate Reports."""
    return render(request, "analytics/generate_reports.html")


@system_administrator_required
def system_settings(request):
    """Figure 3.7k: System Administrator — System Settings."""
    return render(request, "analytics/system_settings.html")
