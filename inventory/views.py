from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from core.permissions import warehouse_officer_required
from inventory.forms import ProductForm, StockAdjustmentForm
from inventory.models import Product, Stock
from orders.models import Order


@warehouse_officer_required
def confirm_fulfilment(request):
    """Figure 3.7f: Warehouse Officer — Confirm Fulfilment."""
    pending_orders = Order.objects.filter(status=Order.Status.CONFIRMED)
    return render(request, "inventory/confirm_fulfilment.html", {"orders": pending_orders})


@warehouse_officer_required
def confirm_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    order.update_status(Order.Status.FULFILLED)
    messages.success(request, f"Order KQ-{order.order_id} marked as fulfilled.")
    return redirect("inventory:confirm_fulfilment")


@warehouse_officer_required
def stock_levels(request):
    """Figure 3.7g: Warehouse Officer — Stock Levels."""
    if request.method == "POST" and "add_product" in request.POST:
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            Stock.objects.create(product=product, quantity_on_hand=0, reorder_level=0)
            messages.success(request, f"{product.name} added to inventory.")
            return redirect("inventory:stock_levels")
    else:
        form = ProductForm()

    stock = Stock.objects.select_related("product").all()
    return render(request, "inventory/stock_levels.html", {"stock": stock, "form": form})


@warehouse_officer_required
def adjust_stock(request, stock_id):
    stock_item = get_object_or_404(Stock, pk=stock_id)
    if request.method == "POST":
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            offset = form.cleaned_data["offset"]
            reason = form.cleaned_data["reason"]
            stock_item.update_level(offset, reason=reason)
            messages.success(request, f"{stock_item.product.name} adjusted by {offset:+d} units.")
    return redirect("inventory:stock_levels")