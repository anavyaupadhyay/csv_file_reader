from io import StringIO
import uuid
import pandas as pd
from django.http import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .tasks import process_images
from .models import ProductImage

class CheckStatusView(APIView):
    def get(self, request, request_id, *args, **kwargs):
        # Check processing status
        images = ProductImage.objects.filter(request_id=request_id)
        if not images.exists():
            return Response({'error': 'Invalid request ID'}, status=status.HTTP_404_NOT_FOUND)

        pending_images = images.filter(processing_status='pending')
        if pending_images.exists():
            return Response({'status': 'in_process'})

        # If all images are processed
        processed_images = images.filter(processing_status='completed')
        df = pd.DataFrame(list(processed_images.values('product__name', 'image_url', 'processed_image_url')))

        if df.empty:
            return Response({'status': 'completed', 'data': []})

        csv_file = StringIO()
        df.to_csv(csv_file, index=False)
        response = HttpResponse(csv_file.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={request_id}.csv'

        return Response({'status': 'completed', 'data': response})
    
class UploadCSVView(APIView):
    def post(self, request, *args, **kwargs):
        if 'file' not in request.FILES:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        csv_file = request.FILES['file']
        if not csv_file.name.endswith('.csv'):
            return Response({'error': 'File is not CSV'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a unique request ID
        request_id = str(uuid.uuid4())
        
        # Save file and trigger asynchronous processing
        file_path = f'/tmp/{request_id}.csv'
        with open(file_path, 'wb+') as f:
            for chunk in csv_file.chunks():
                f.write(chunk)

        # Trigger the task
        process_images.delay(request_id)
        
        return Response({'request_id': request_id})

class WebhookTriggerView(APIView):
    def post(self, request, *args, **kwargs):
        # Logic to create and send the CSV file
        df = pd.DataFrame(list(ProductImage.objects.values('product__name', 'image_url', 'processed_image_url')))
        csv_file = StringIO()
        df.to_csv(csv_file, index=False)
        response = HttpResponse(csv_file.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=processed_images.csv'
        
        return response
