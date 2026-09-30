from django.contrib import messages
from django.db import models, transaction
from django.shortcuts import get_object_or_404, redirect, render

from core.permissions import sales_agent_required
from orders.forms import CustomerForm, OrderForm, OrderItemFormSet
from orders.models import Customer, Invoice, Order


@sales_agent_required
def create_order(request):
    """Figure 3.7b: Sales Agent — Create Order (fully functional)."""
    if request.method == "POST":
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            with transaction.atomic():
                order = order_form.save(commit=False)
                order.created_by = request.user
                order.save()

                item_formset = OrderItemFormSet(request.POST, instance=order)
                if item_formset.is_valid():
                    items = item_formset.save(commit=False)
                    for item in items:
                        item.unit_price = item.product.unit_price
                        item.save()
                    # Delete any items marked for deletion
                    for obj in item_formset.deleted_objects:
                        obj.delete()

                    messages.success(
                        request,
                        f"Order KQ-{order.order_id} created successfully "
                        f"with {len(items)} item(s).",
                    )
                    return redirect("orders:order_detail", order_id=order.order_id)
                else:
                    # If items are invalid, delete the partially created order
                    order.delete()
                    messages.error(request, "Please add at least one valid item.")
        else:
            item_formset = OrderItemFormSet(request.POST)
    else:
        order_form = OrderForm()
        item_formset = OrderItemFormSet()

    return render(
        request,
        "orders/create_order.html",
        {"order_form": order_form, "item_formset": item_formset},
    )


@sales_agent_required
def track_orders(request):
    """Figure 3.7c: Sales Agent — Track Orders."""
    query = request.GET.get("q", "").strip()
    orders = Order.objects.select_related("customer").all()
    if query:
        orders = orders.filter(
            models.Q(customer__name__icontains=query)
            | models.Q(order_id__icontains=query)
        )
    return render(request, "orders/track_orders.html", {"orders": orders, "query": query})


@sales_agent_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related("customer").prefetch_related("items__product"),
        pk=order_id,
    )
    return render(request, "orders/order_detail.html", {"order": order})


@sales_agent_required
def confirm_order(request, order_id):
    """Sales Agent confirms a pending order — moves it to 'confirmed' status."""
    order = get_object_or_404(Order, pk=order_id)
    if order.status == Order.Status.PENDING:
        order.update_status(Order.Status.CONFIRMED)
        messages.success(request, f"Order KQ-{order.order_id} confirmed.")
    else:
        messages.warning(request, f"Order KQ-{order.order_id} is already {order.get_status_display()}.")
    return redirect("orders:order_detail", order_id=order.order_id)


@sales_agent_required
def customer_records(request):
    """Figure 3.7d: Sales Agent — Customer Records."""
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer added successfully.")
            return redirect("orders:customer_records")
    else:
        form = CustomerForm()

    query = request.GET.get("q", "").strip()
    customers = Customer.objects.all()
    if query:
        customers = customers.filter(
            models.Q(name__icontains=query)
            | models.Q(contact_info__icontains=query)
            | models.Q(account_type__icontains=query)
        )

    return render(
        request,
        "orders/customer_records.html",
        {"customers": customers, "form": form, "query": query},
    )


@sales_agent_required
def customer_order_history(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    orders = customer.orders.all()
    return render(
        request,
        "orders/customer_order_history.html",
        {"customer": customer, "orders": orders},
    )


@sales_agent_required
def generate_invoice(request, order_id):
    """Figure 3.7e: Sales Agent — Generate Invoice."""
    order = get_object_or_404(
        Order.objects.select_related("customer").prefetch_related("items__product"),
        pk=order_id,
    )

    # Calculate totals
    items = order.items.all()
    subtotal = sum(item.line_total for item in items)
    vat = subtotal * 16 / 100
    total = subtotal + vat

    # If POST, actually generate the invoice record
    if request.method == "POST":
        if hasattr(order, "invoice"):
            messages.info(request, "Invoice already exists for this order.")
        else:
            invoice = Invoice.generate(order)
            messages.success(request, f"Invoice #{invoice.invoice_id} generated successfully.")
        return redirect("orders:generate_invoice", order_id=order.order_id)

    # Check if invoice already exists
    existing_invoice = getattr(order, "invoice", None)

    return render(
        request,
        "orders/generate_invoice.html",
        {
            "order": order,
            "items": items,
            "subtotal": subtotal,
            "vat": vat,
            "total": total,
            "existing_invoice": existing_invoice,
        },
    )
