"""
Application runner with system checks
"""
import os
import sys
import logging
import subprocess
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        ('streamlit', 'streamlit'),
        ('boto3', 'boto3'),
        ('pandas', 'pandas'),
        ('python-dotenv', 'dotenv')
    ]
    
    missing = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)
    
    if missing:
        logger.error(f"Missing packages: {', '.join(missing)}")
        logger.info(f"Install with: pip install {' '.join(missing)}")
        return False
    
    logger.info("All required packages are installed")
    return True


def check_aws_config():
    """Check AWS configuration"""
    region = os.getenv('AWS_REGION')
    bucket = os.getenv('S3_BUCKET_NAME')
    
    if not region or not bucket:
        logger.error("AWS configuration missing")
        logger.info("Please set AWS_REGION and S3_BUCKET_NAME in .env file")
        return False
    
    logger.info(f"AWS configuration found - Region: {region}, Bucket: {bucket}")
    return True


def test_system():
    """Test system initialization"""
    try:
        from src import RAGSystem
        
        logger.info("Testing system initialization...")
        rag = RAGSystem()
        
        # Test with simple query
        response = rag.query("Hello")
        if response:
            logger.info("System test passed")
            logger.info(f"Products loaded: {len(rag.products)}")
            return True
        else:
            logger.error("System test failed")
            return False
            
    except Exception as e:
        logger.error(f"System test failed: {str(e)}")
        return False


def main():
    """Main runner"""
    logger.info("Home Decor RAG Chatbot")
    logger.info("=" * 50)
    
    # Run checks
    if not check_requirements():
        sys.exit(1)
    
    if not check_aws_config():
        sys.exit(1)
    
    if not test_system():
        sys.exit(1)
    
    logger.info("All checks passed - starting application...")
    
    # Start Streamlit app
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501"
        ])
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
