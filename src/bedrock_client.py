"""
Amazon Bedrock client for LLM integration
"""
import boto3
import json
import logging
import os
import time
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class BedrockClient:
    """Amazon Bedrock LLM client"""
    
    def __init__(self):
        """Initialize Bedrock client"""
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.model_id = "meta.llama3-70b-instruct-v1:0"
        self.client = None
        self.is_available = False
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize and test Bedrock client"""
        try:
            self.client = boto3.client(
                'bedrock-runtime',
                region_name=self.region
            )
            
            if self._test_model():
                self.is_available = True
                logger.info("Bedrock client initialized successfully")
            else:
                self._show_setup_instructions()
                raise Exception("Bedrock model access required")
                
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock: {str(e)}")
            self._show_setup_instructions()
            raise
    
    def _test_model(self) -> bool:
        """Test model availability"""
        try:
            request_body = {
                "prompt": "Hello",
                "max_gen_len": 10,
                "temperature": 0.1
            }
            
            self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body),
                contentType='application/json',
                accept='application/json'
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Model test failed: {str(e)[:100]}")
            return False
    
    def _show_setup_instructions(self):
        """Display setup instructions"""
        print("\n" + "="*60)
        print("AMAZON BEDROCK SETUP REQUIRED")
        print("="*60)
        print("1. Go to AWS Bedrock Console")
        print("2. Enable 'Llama 3 70B Instruct' model access")
        print("3. Add bedrock:InvokeModel permission to your IAM user")
        print("4. Restart the application")
        print("="*60)
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response using Llama3 70B"""
        if not self.is_available:
            raise Exception("Bedrock client not available")
        
        try:
            system_prompt = """You are a home decor assistant. Help customers find furniture, lighting, and decor items.

Instructions:
1. For greetings, respond naturally and ask how you can help
2. For product queries, use the provided context to give recommendations
3. Be helpful and knowledgeable about home decor
4. Ask follow-up questions to understand needs better

Product Context:
{context}

User Query: {prompt}

Response:"""

            full_prompt = system_prompt.format(context=context, prompt=prompt)
            
            request_body = {
                "prompt": full_prompt,
                "max_gen_len": 1000,
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            # Realistic processing delay
            time.sleep(7)
            
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body),
                contentType='application/json',
                accept='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            generated_text = response_body.get('generation', '')

            # Clean and format the response
            cleaned_text = self._clean_response_text(generated_text)

            return cleaned_text
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise

    def _clean_response_text(self, text: str) -> str:
        """Clean and format response text to fix encoding/formatting issues"""
        if not text:
            return ""

        import re

        # First check if text is malformed before applying aggressive fixes
        if not self._is_text_malformed(text):
            # Text looks normal, just do basic cleanup
            text = re.sub(r'\s+', ' ', text)  # Fix multiple spaces
            text = re.sub(r'\s+([,.!?;:])', r'\1', text)  # Fix punctuation spacing
            text = re.sub(r'([,.!?;:])\s*', r'\1 ', text)
            return text.strip()

        # Text appears malformed, apply fixes

        # Fix price formatting issues like "299.99)w" -> "299.99) w"
        text = re.sub(r'(\$?\d+\.?\d*)\)([a-zA-Z])', r'\1) \2', text)

        # Fix mathematical symbols and special characters
        text = re.sub(r'\s*−\s*', ' - ', text)  # Fix minus signs
        text = re.sub(r'\s*\$\s*', '$', text)   # Fix dollar signs

        # Fix word breaks like "w i t h" -> "with" (only for obvious cases)
        # Look for patterns of single letters separated by spaces
        text = re.sub(r'\b([a-zA-Z])\s+([a-zA-Z])\s+([a-zA-Z])\s+([a-zA-Z])\s+([a-zA-Z])\b', r'\1\2\3\4\5', text)
        text = re.sub(r'\b([a-zA-Z])\s+([a-zA-Z])\s+([a-zA-Z])\s+([a-zA-Z])\b', r'\1\2\3\4', text)
        text = re.sub(r'\b([a-zA-Z])\s+([a-zA-Z])\s+([a-zA-Z])\b', r'\1\2\3', text)

        # Only fix single letter pairs if they look like broken words
        # Be more conservative here
        text = re.sub(r'\b([a-z])\s+([a-z])\b(?=\s+[a-z]\s)', r'\1\2', text)

        # Fix multiple spaces
        text = re.sub(r'\s+', ' ', text)

        # Fix punctuation spacing
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)
        text = re.sub(r'([,.!?;:])\s*', r'\1 ', text)

        # Fix parentheses spacing
        text = re.sub(r'\s*\(\s*', ' (', text)
        text = re.sub(r'\s*\)\s*', ') ', text)

        # Clean up extra whitespace
        text = ' '.join(text.split())

        return text.strip()

    def _is_text_malformed(self, text: str) -> bool:
        """Check if text appears to have formatting issues"""
        if not text:
            return False

        import re

        # Check for excessive single character words (like "w i t h")
        words = text.split()
        single_char_count = sum(1 for word in words if len(word) == 1 and word.isalpha())

        # If more than 15% of words are single characters, likely malformed
        if len(words) > 5 and (single_char_count / len(words)) > 0.15:
            return True

        # Check for specific malformed patterns
        # Pattern like "299.99)w" (price followed by letter without space)
        if re.search(r'\d+\.?\d*\)[a-zA-Z]', text):
            return True

        # Pattern like "w i t h" (3+ single letters in sequence)
        if re.search(r'\b[a-zA-Z]\s+[a-zA-Z]\s+[a-zA-Z]\s+[a-zA-Z]', text):
            return True

        # Pattern with weird spacing in common words
        malformed_patterns = [
            r'w\s+i\s+t\s+h',
            r's\s+h\s+o\s+w',
            r's\s+t\s+o\s+p',
            r'c\s+h\s+a\s+n\s+d\s+e\s+l\s+i\s+e\s+r'
        ]

        for pattern in malformed_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    def _basic_text_cleanup(self, text: str) -> str:
        """Basic cleanup for severely malformed text"""
        import re

        # Try to reconstruct words by removing spaces between single characters
        # This is a more aggressive approach for badly formatted text
        words = text.split()
        cleaned_words = []
        current_word = ""

        for word in words:
            if len(word) == 1 and word.isalpha():
                current_word += word
            else:
                if current_word:
                    cleaned_words.append(current_word)
                    current_word = ""
                cleaned_words.append(word)

        if current_word:
            cleaned_words.append(current_word)

        return ' '.join(cleaned_words)
