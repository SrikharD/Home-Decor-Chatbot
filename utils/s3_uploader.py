"""
S3 uploader utility for sample documents
"""
import boto3
import zipfile
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def upload_sample_docs():
    """Upload sample catalog files to S3"""
    try:
        # Configuration
        bucket_name = os.getenv('S3_BUCKET_NAME', 'home-decor-chatbot')
        
        # Create S3 client
        s3_client = boto3.client('s3')
        
        # Create zip file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f'sample_docs_{timestamp}.zip'
        
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            # Add CSV files
            for root, dirs, files in os.walk('sample_catalogs'):
                for file in files:
                    if file.endswith('.csv'):
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, file_path)
            
            # Add README
            readme_content = """# Home Decor Product Catalog

This draft contains sample product catalogs for the home decor chatbot:

- bedroom_furniture.csv: Bedroom furniture items
- kitchen_dining.csv: Kitchen and dining room items  
- living_room.csv: Living room furniture and decor

Total products: 30 items across all categories.
"""
            zipf.writestr('README.md', readme_content)
        
        # Upload to S3
        s3_key = f'sample_docs/{zip_filename}'
        s3_client.upload_file(zip_filename, bucket_name, s3_key)
        
        # Make publicly readable
        s3_client.put_object_acl(
            Bucket=bucket_name,
            Key=s3_key,
            ACL='public-read'
        )
        
        # Clean up local zip
        os.remove(zip_filename)
        
        # Generate URL
        url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
        
        print(f"Upload successful!")
        print(f"Public URL: {url}")
        print(f"File size: {os.path.getsize(zip_filename) if os.path.exists(zip_filename) else 'N/A'} bytes")
        
        return url
        
    except Exception as e:
        print(f"Upload failed: {str(e)}")
        return None


if __name__ == "__main__":
    upload_sample_docs()
