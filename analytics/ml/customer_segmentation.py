"""
Customer segmentation module.

Implements RFM (Recency, Frequency, Monetary)-based k-means clustering
to segment customers by purchasing behaviour, as reviewed in Chapter 2
(Customer Sales Trend Analysis).
"""


import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from django.utils import timezone

def segment_customers(customer_queryset):
    """
    Compute RFM scores per customer and cluster them with k-means.
    """
    try:
        if not customer_queryset.exists():
            return []

        data = []
        now = timezone.now()
        for customer in customer_queryset:
            orders = customer.orders.all()
            if not orders.exists():
                continue
            
            recent_order = orders.order_by('-order_date').first()
            recency = (now - recent_order.order_date).days
            frequency = orders.count()
            monetary = sum(
                item.quantity * item.unit_price 
                for order in orders 
                for item in order.items.all()
            )
            data.append({
                'customer_id': customer.customer_id,
                'customer_name': customer.name,
                'recency': recency,
                'frequency': frequency,
                'monetary': float(monetary)
            })

        if len(data) < 3:
            return data

        df = pd.DataFrame(data)
        features = df[['recency', 'frequency', 'monetary']]
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        
        k = min(3, len(df))
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        df['cluster'] = kmeans.fit_predict(scaled_features)
        
        cluster_means = df.groupby('cluster')[['recency', 'frequency', 'monetary']].mean()
        sorted_clusters = cluster_means.sort_values('monetary', ascending=False).index.tolist()
        
        labels = ['VIP/High-Volume', 'Regular', 'At-Risk/Dormant']
        cluster_to_label = {}
        for i, cluster in enumerate(sorted_clusters):
            cluster_to_label[cluster] = labels[i] if i < len(labels) else 'Regular'
            
        df['cluster_label'] = df['cluster'].map(cluster_to_label)
        return df.drop(columns=['cluster']).to_dict('records')
    except Exception as e:
        return []
