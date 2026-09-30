import os
import random
from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from orders.models import Customer, Order, OrderItem
from inventory.models import Product, Stock

class Command(BaseCommand):
    help = 'Seeds the database with demo data for ML models'

    def handle(self, *args, **kwargs):
        # 1. Clear existing data
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Stock.objects.all().delete()
        Product.objects.all().delete()
        Customer.objects.all().delete()
        
        # 2. Create Products & Stock
        product_names = [
            ("500ml Bottle Case (24 Pack)", 1200.00),
            ("1L Bottle Case (12 Pack)", 1800.00),
            ("5L Jerrycan", 350.00),
            ("20L Dispenser Bottle", 1800.00),
            ("250ml Cups Case (48 Pack)", 960.00),
            ("Premium Glass 500ml (12 Pack)", 3600.00),
            ("Flavored Water 500ml Case (24 Pack)", 1440.00),
            ("10L Bulk Dispenser Box", 900.00),
        ]
        products = []
        for name, price in product_names:
            p = Product.objects.create(name=name, unit_price=price)
            Stock.objects.create(product=p, quantity_on_hand=random.randint(100, 1000), reorder_level=50)
            products.append(p)

        # 3. Create Customers
        account_types = ["KQ Internal Department", "Corporate Client", "Government Entity", "Distributor"]
        customers = []
        for i in range(15):
            c = Customer.objects.create(
                name=f"Customer {i+1}",
                contact_info=f"contact{i+1}@example.com",
                account_type=random.choice(account_types)
            )
            customers.append(c)
            
        # 4. Create Orders
        now = timezone.now()
        statuses = [Order.Status.PENDING, Order.Status.CONFIRMED, Order.Status.FULFILLED, Order.Status.INVOICED]
        
        for _ in range(250):
            customer = random.choice(customers)
            # Random date within last 365 days
            days_ago = random.randint(0, 365)
            order_date = now - timedelta(days=days_ago)
            
            order = Order.objects.create(
                customer=customer,
                status=random.choice(statuses)
            )
            # Update order_date (auto_now_add overrides on create)
            Order.objects.filter(pk=order.pk).update(order_date=order_date)
            
            # Add items
            for _ in range(random.randint(1, 5)):
                product = random.choice(products)
                quantity = random.randint(1, 50)
                if random.random() < 0.05:
                    quantity = random.randint(200, 500) # Anomalous quantity
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=product.unit_price
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded demo data.'))
