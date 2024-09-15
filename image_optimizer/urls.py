from django.urls import path
from .views import UploadCSVView, CheckStatusView, WebhookTriggerView

urlpatterns = [
    path('upload/', UploadCSVView.as_view(), name='upload_csv'),
    path('status/<str:request_id>/', CheckStatusView.as_view(), name='check_status'),
    path('webhook/', WebhookTriggerView.as_view(), name='webhook_trigger'),
]
