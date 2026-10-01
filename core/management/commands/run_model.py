from django.core.management.base import BaseCommand
from orders.models import Order, Customer
from analytics.ml.forecasting import forecast_demand
from analytics.ml.customer_segmentation import segment_customers
from analytics.ml.anomaly_detection import detect_anomalies


class Command(BaseCommand):
    help = "Run and inspect any of the 3 machine learning models individually."

    def add_arguments(self, parser):
        parser.add_argument(
            "model_name",
            type=str,
            choices=["forecast", "segmentation", "anomaly", "all"],
            help="Name of the model to run: 'forecast', 'segmentation', 'anomaly', or 'all'",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=10,
            help="Number of result rows to display (default: 10)",
        )

    def handle(self, *args, **options):
        model_name = options["model_name"]
        limit = options["limit"]

        if model_name in ["forecast", "all"]:
            self.run_forecasting(limit)

        if model_name in ["segmentation", "all"]:
            self.run_segmentation(limit)

        if model_name in ["anomaly", "all"]:
            self.run_anomaly(limit)

    def run_forecasting(self, limit):
        self.stdout.write(self.style.MIGRATE_HEADING("\n" + "=" * 65))
        self.stdout.write(self.style.MIGRATE_HEADING("  MODEL 1: DEMAND FORECASTING (SARIMAX)"))
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 65))
        self.stdout.write("  File:       analytics/ml/forecasting.py")
        self.stdout.write("  Algorithm:  SARIMAX(order=(1,1,1), seasonal_order=(0,0,0,0))")
        self.stdout.write("  Data Source: SQLite DB -> 'orders_orderitem' & 'orders_order'")
        self.stdout.write("  Target:     Daily aggregate order volume (units / litres)")
        self.stdout.write("-" * 65)

        orders = Order.objects.all()
        total_orders = orders.count()
        self.stdout.write(f"  Ingesting {total_orders} historical orders from database...")

        results = forecast_demand(orders, periods=30)
        if not results:
            self.stdout.write(self.style.WARNING("  Insufficient data for forecasting."))
            return

        self.stdout.write(self.style.SUCCESS(f"  Generated 30-day forecast. Showing first {limit} days:\n"))
        self.stdout.write(f"  {'Forecast Date':<15} | {'Predicted Volume (Units/Litres)':<30}")
        self.stdout.write("  " + "-" * 50)
        for r in results[:limit]:
            self.stdout.write(f"  {r['date']:<15} | {r['predicted_quantity']:<30.1f}")
        self.stdout.write(f"\n  [Status: Successfully trained and forecasted using statsmodels SARIMAX]")

    def run_segmentation(self, limit):
        self.stdout.write(self.style.MIGRATE_HEADING("\n" + "=" * 65))
        self.stdout.write(self.style.MIGRATE_HEADING("  MODEL 2: CUSTOMER SEGMENTATION (RFM + K-MEANS)"))
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 65))
        self.stdout.write("  File:       analytics/ml/customer_segmentation.py")
        self.stdout.write("  Algorithm:  K-Means Clustering (k=3) with StandardScaler")
        self.stdout.write("  Data Source: SQLite DB -> 'orders_customer' & transaction history")
        self.stdout.write("  Features:   Recency (days), Frequency (order count), Monetary (KSh)")
        self.stdout.write("-" * 65)

        customers = Customer.objects.prefetch_related("orders__items").all()
        self.stdout.write(f"  Evaluating {customers.count()} customer accounts...")

        results = segment_customers(customers)
        if not results:
            self.stdout.write(self.style.WARNING("  Insufficient data for segmentation."))
            return

        self.stdout.write(self.style.SUCCESS(f"  Segmented {len(results)} accounts. Showing top {limit}:\n"))
        self.stdout.write(f"  {'Customer Name':<32} | {'Recency':<8} | {'Freq':<6} | {'Monetary (KSh)':<16} | {'Segment':<18}")
        self.stdout.write("  " + "-" * 90)
        for s in results[:limit]:
            self.stdout.write(
                f"  {s['customer_name'][:32]:<32} | "
                f"{s['recency']:<8} | "
                f"{s['frequency']:<6} | "
                f"KSh {s['monetary']:<12,.2f} | "
                f"{s['cluster_label']:<18}"
            )
        self.stdout.write(f"\n  [Status: Successfully clustered using scikit-learn KMeans]")

    def run_anomaly(self, limit):
        self.stdout.write(self.style.MIGRATE_HEADING("\n" + "=" * 65))
        self.stdout.write(self.style.MIGRATE_HEADING("  MODEL 3: ORDER ANOMALY DETECTION (ISOLATION FOREST)"))
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 65))
        self.stdout.write("  File:       analytics/ml/anomaly_detection.py")
        self.stdout.write("  Algorithm:  Isolation Forest (contamination=0.05)")
        self.stdout.write("  Data Source: SQLite DB -> 'orders_order' & 'orders_orderitem'")
        self.stdout.write("  Features:   Quantity, Total Order Value (KSh), Customer Order Frequency")
        self.stdout.write("-" * 65)

        orders = Order.objects.select_related("customer").prefetch_related("items__product").all()
        self.stdout.write(f"  Scanning {orders.count()} order records for irregularities...")

        results = detect_anomalies(orders)
        if not results:
            self.stdout.write(self.style.SUCCESS("  No anomalies detected in the dataset."))
            return

        self.stdout.write(self.style.WARNING(f"  Found {len(results)} flagged anomalous orders. Showing first {limit}:\n"))
        self.stdout.write(f"  {'Order ID':<10} | {'Customer Name':<32} | {'Anomaly Score':<15} | {'Decision':<10}")
        self.stdout.write("  " + "-" * 75)
        for a in results[:limit]:
            self.stdout.write(
                f"  KQ-{a['order_id']:<7} | "
                f"{a['customer_name'][:32]:<32} | "
                f"{a['anomaly_score']:<15.4f} | "
                f"FLAGGED"
            )
        self.stdout.write(f"\n  [Status: Outliers successfully isolated using scikit-learn IsolationForest]")
