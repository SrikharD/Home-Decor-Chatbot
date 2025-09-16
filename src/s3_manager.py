"""
S3 document manager for product catalog
"""
import boto3
import pandas as pd
import zipfile
import io
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class S3Manager:
    """Manage product catalog from S3"""
    
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.client = boto3.client('s3')
        self.products = []
        
        logger.info(f"S3 manager initialized for bucket: {bucket_name}")
        self.load_catalog()
    
    def load_catalog(self):
        """Load product catalog from S3"""
        try:
            logger.info("Loading product catalog from S3")
            
            # List objects in sample_docs folder
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='sample_docs/'
            )
            
            if 'Contents' not in response:
                raise Exception("No sample_docs found in S3 bucket")
            
            # Find latest zip file
            zip_files = [obj for obj in response['Contents'] if obj['Key'].endswith('.zip')]
            if not zip_files:
                raise Exception("No zip files found")
            
            latest_zip = max(zip_files, key=lambda x: x['LastModified'])
            zip_key = latest_zip['Key']
            
            # Download and extract
            zip_obj = self.client.get_object(Bucket=self.bucket_name, Key=zip_key)
            zip_content = zip_obj['Body'].read()
            
            self.products = []
            with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
                for file_name in zip_file.namelist():
                    if file_name.endswith('.csv') and 'sample_catalogs' in file_name:
                        with zip_file.open(file_name) as csv_file:
                            df = pd.read_csv(csv_file)
                            products_from_file = df.to_dict('records')
                            self.products.extend(products_from_file)
            
            logger.info(f"Loaded {len(self.products)} products from S3")
            
        except Exception as e:
            logger.error(f"Failed to load catalog: {str(e)}")
            raise
    
    def search_products(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for relevant products"""
        query_lower = query.lower()
        
        # Skip search for casual greetings
        greetings = ['hi', 'hello', 'hai', 'hey']
        if any(greeting in query_lower for greeting in greetings) and len(query.split()) <= 3:
            return []
        
        matching_products = []
        
        for product in self.products:
            score = 0
            searchable_text = ' '.join(str(product.get(field, '')) for field in [
                'Product_Name', 'Description', 'Category', 'Subcategory', 'Room', 'Style'
            ]).lower()
            
            # Score based on keyword matches
            query_words = query_lower.split()
            for word in query_words:
                if word in searchable_text:
                    score += searchable_text.count(word)
            
            # Category boost
            if 'lighting' in query_lower and 'lighting' in product.get('Category', '').lower():
                score += 10
            if 'furniture' in query_lower and 'furniture' in product.get('Category', '').lower():
                score += 10
            
            if score > 0:
                product_copy = product.copy()
                product_copy['relevance_score'] = score
                matching_products.append(product_copy)
        
        # Sort by relevance
        matching_products.sort(key=lambda x: x['relevance_score'], reverse=True)
        return matching_products[:max_results]
