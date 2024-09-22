from django.db import models

# Create your models here.

class Product(models.Model):
    #  TODO:: can add more properties to product as per requirements]
    name = models.CharField(max_length=255)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image_url = models.URLField()
    processed_image_url = models.URLField(null=True, blank=True)
    processing_status = models.CharField(max_length=50, default='pending')
    request_id = models.CharField(max_length=255)  # Track request ID
    error_message = models.TextField(null=True, blank=True)


