"""
RAG system for home decor chatbot
"""
import os
import logging
from typing import List, Dict
from .bedrock_client import BedrockClient
from .s3_manager import S3Manager

logger = logging.getLogger(__name__)


class RAGSystem:
    """Main RAG system for home decor chatbot"""
    
    def __init__(self):
        """Initialize RAG system"""
        try:
            # Initialize components
            self.llm = BedrockClient()
            
            bucket_name = os.getenv('S3_BUCKET_NAME', 'home-decor-chatbot')
            self.s3_manager = S3Manager(bucket_name)
            
            logger.info(f"RAG system initialized with {len(self.s3_manager.products)} products")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {str(e)}")
            raise
    
    @property
    def products(self):
        """Get product list"""
        return self.s3_manager.products
    
    def query(self, prompt: str) -> str:
        """Process user query"""
        try:
            # Search for relevant products
            relevant_products = self.s3_manager.search_products(prompt)
            
            # Format context
            context = ""
            if relevant_products:
                context = "Available Products:\n\n"
                for i, product in enumerate(relevant_products, 1):
                    context += f"{i}. {product.get('Product_Name', 'N/A')} - ${product.get('Price', 'N/A')}\n"
                    context += f"   Category: {product.get('Category', 'N/A')}, Room: {product.get('Room', 'N/A')}\n"
                    context += f"   Description: {product.get('Description', 'N/A')}\n\n"
            
            # Generate response
            response = self.llm.generate_response(prompt, context)
            
            logger.info(f"Generated response for query: {prompt[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Query processing failed: {str(e)}")
            raise
