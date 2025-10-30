from django.urls import path
from .views import InvoiceCreateView, InvoiceDetailView, PaymentListView

app_name = "payments"

urlpatterns = [
    path("invoices/create/", InvoiceCreateView.as_view(), name="invoice-create"),
    path("invoices/get-one/<uuid:pk>/", InvoiceDetailView.as_view(), name="invoice-detail"),
    path("payments/", PaymentListView.as_view(), name="payment-list"),
]
