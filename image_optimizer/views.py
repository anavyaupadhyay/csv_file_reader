from io import StringIO
import uuid
import pandas as pd
from django.http import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .utils import generate_csv
from .tasks import process_images
from .models import ProductImage

class CheckStatusView(APIView):
    def get(self, request, request_id, *args, **kwargs):
        # Get images for the request_id
        images = ProductImage.objects.filter(request_id=request_id)
        
        if not images.exists():
            return Response({'error': 'Invalid request ID'}, status=status.HTTP_404_NOT_FOUND)

        # Check if there are any images still in 'pending' state
        pending_images = images.filter(processing_status='pending')
        if pending_images.exists():
            return Response({'status': 'in_process'})
        
        # Check if any images have failed
        failed_images = images.filter(processing_status='failed')
        if failed_images.exists():
            errors = list(failed_images.values('image_url', 'error_message'))
        else:
            errors = []

        processed_images = images.filter(processing_status='completed')
        if failed_images.exists() and not processed_images.exists(): # Means all the images are failed to processed
            return Response({'status': 'failed', 'errors': list(failed_images.values('image_url', 'error_message'))})
        
        # images are processed, so prepare the response with processed data
        response = generate_csv(processed_images)

        return Response({'status': 'completed', 'data': response, 'errors': list(failed_images.values('image_url', 'error_message')) })


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
        response = generate_csv(ProductImage.objects.filter(status="completed"))
        return response
