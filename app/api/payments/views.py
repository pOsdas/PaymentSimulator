from drf_spectacular.types import OpenApiTypes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .serializers import InvoiceCreateSerializer, InvoiceSerializer, PaymentSerializer
from app.models import Invoice, Payment
from app.api.celery_tasks import process_invoice_task
from drf_spectacular.utils import extend_schema, OpenApiParameter


class InvoiceCreateView(APIView):

    @extend_schema(
        tags=["Payments"],
        request=InvoiceCreateSerializer,
        responses=InvoiceSerializer,
    )
    def post(self, request, *args, **kwargs):
        serializer = InvoiceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invoice = serializer.save()
        process_invoice_task.delay(str(invoice.id))
        out = InvoiceSerializer(invoice)
        return Response(out.data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Payments"])
class InvoiceDetailView(generics.RetrieveAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    lookup_field = "pk"


@extend_schema(tags=["Payments"])
class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.select_related("invoice").all()
    serializer_class = PaymentSerializer


