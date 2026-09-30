import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from orders.models import Order, Customer
from analytics.ml.forecasting import forecast_demand
from analytics.ml.customer_segmentation import segment_customers
from analytics.ml.anomaly_detection import detect_anomalies

print("Testing forecasting...")
res1 = forecast_demand(Order.objects.all(), periods=5)
print(f"Forecast rows: {len(res1)}")

print("Testing segmentation...")
res2 = segment_customers(Customer.objects.all())
print(f"Segmentation rows: {len(res2)}")

print("Testing anomaly detection...")
res3 = detect_anomalies(Order.objects.all())
print(f"Anomaly rows: {len(res3)}")
