from django import forms
from django.forms import inlineformset_factory

from inventory.models import Product
from orders.models import Customer, Order, OrderItem


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["name", "contact_info", "account_type"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Nairobi Logistics Hub",
            }),
            "contact_info": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Email or phone number",
            }),
            "account_type": forms.Select(
                choices=[
                    ("", "Select account type..."),
                    ("Corporate", "Corporate"),
                    ("Government", "Government"),
                    ("Distributor", "Distributor"),
                    ("Internal Department", "Internal Department"),
                ],
                attrs={"class": "form-select"},
            ),
        }


class OrderForm(forms.ModelForm):
    """Select a customer for a new order."""

    class Meta:
        model = Order
        fields = ["customer"]
        widgets = {
            "customer": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["customer"].queryset = Customer.objects.all()
        self.fields["customer"].empty_label = "Select a customer..."


class OrderItemForm(forms.ModelForm):
    """A single line item in an order."""

    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "1",
                "placeholder": "Qty",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Product.objects.all()
        self.fields["product"].empty_label = "Select product..."

    def save(self, commit=True):
        item = super().save(commit=False)
        # Auto-fill unit_price from the product's current price
        if item.product_id:
            item.unit_price = item.product.unit_price
        if commit:
            item.save()
        return item


# Inline formset: lets us handle multiple order items on the same page
OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True,
)
