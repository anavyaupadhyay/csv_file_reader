from celery import shared_task
from PIL import Image
import requests
from io import BytesIO
from .models import Product, ProductImage

@shared_task
def process_images(request_id):
    import pandas as pd
    # Retrieve and process the CSV file related to request_id (implement file retrieval based on your storage)
    # This is a placeholder for the actual file processing
    df = pd.read_csv(f'/tmp/{request_id}.csv')

    for _, row in df.iterrows():
        product, created = Product.objects.get_or_create(
            serial_number=row['Serial Number'],
            defaults={'name': row['Product Name']}
        )
        urls = row['Input Image Urls'].split(',')
        for url in urls:
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            # Compress image
            output = BytesIO()
            img.save(output, format='JPEG', quality=50)
            # Save processed image to a server or a cloud storage and get the URL
            processed_url = 'url_to_processed_image'
            
            ProductImage.objects.create(
                product=product,
                image_url=url,
                processed_image_url=processed_url,
                processing_status='completed',
                request_id=request_id
            )

    # Trigger webhook here if needed
