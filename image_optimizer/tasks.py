from celery import shared_task
from PIL import Image
import requests
from io import BytesIO
from .models import Product, ProductImage

import pandas as pd


@shared_task(bind=True, max_retries=2)
def process_images(self, request_id):
    try:
        # Retrieve the CSV file related to request_id
        file_path = f'/tmp/{request_id}.csv'
        df = pd.read_csv(file_path)

        for _, row in df.iterrows():
            # Create or get the product
            product, created = Product.objects.get_or_create(name=row['Product Name'])

            # Process each image URL
            urls = row['Input Image Urls'].split(',')
            process_image_urls(self, request_id, product, urls)

    except Exception as e:
        print(f"Error processing CSV file: {e}")
        # Optionally, log this error or take additional actions

        # Here we're just logging it and not modifying the database records
   


def process_image_urls(self, request_id, product, urls):
    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Ensure we raise an error for bad responses
            img = Image.open(BytesIO(response.content))

                    # Compress the image
            output = BytesIO()
            img.save(output, format='JPEG', quality=50)
            processed_image_url = 'url_to_processed_image'  # Update this to where the image is saved

                    # Save image data to the database
            ProductImage.objects.create(
                        product=product,
                        image_url=url,
                        processed_image_url=processed_image_url,
                        processing_status='completed',
                        request_id=request_id
                    )
        except Exception as e:
                    # Log the error and retry
            print(f"Error processing image {url}: {e}")
            if self.request.retries < self.max_retries:
                raise self.retry(countdown=5)  # Retry after 5 seconds
            else:
                ProductImage.objects.create(
                            product=product,
                            image_url=url,
                            processed_image_url=None,
                            processing_status='failed',
                            request_id=request_id,
                            error_message=str(e)  # Save the error message
                        )