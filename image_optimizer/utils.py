from io import StringIO
from django.http import HttpResponse
import pandas as pd

def generate_csv(processed_images):
    df = pd.DataFrame(list(processed_images.values('product__name', 'image_url', 'processed_image_url')))
        
    if df.empty:
        return []
    
    # Add serial number column
    df.reset_index(drop=True, inplace=True)
    df.index += 1
    df.index.name = 'S.No.'
    
    # Generate CSV file
    csv_file = StringIO()
    df.to_csv(csv_file, index=True)
    response = HttpResponse(csv_file.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=processed_images.csv'

    return response