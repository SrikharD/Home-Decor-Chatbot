# Home Decor RAG Chatbot

A professional home decor assistant powered by Amazon Bedrock Llama3 70B and S3.

## Project Structure

```
├── src/                    # Core application modules
│   ├── __init__.py        # Package initialization
│   ├── bedrock_client.py  # Amazon Bedrock LLM client
│   ├── s3_manager.py      # S3 document management
│   └── rag_system.py      # Main RAG system
├── utils/                 # Utility scripts
│   └── s3_uploader.py     # Upload sample docs to S3
├── sample_catalogs/       # Product catalog CSV files
│   ├── bedroom_furniture.csv
│   ├── kitchen_dining.csv
│   └── living_room.csv
├── app.py                 # Streamlit web application
├── run.py                 # Application runner with checks
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables (not in repo)
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure AWS credentials in .env:**
   ```
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=home-decor-chatbot
   ```

3. **Enable Bedrock access:**
   - Go to AWS Bedrock Console
   - Enable Llama 3 70B Instruct model
   - Add bedrock:InvokeModel permission to IAM user

4. **Upload sample data:**
   ```bash
   python utils/s3_uploader.py
   ```

## Usage

**Run the application:**
```bash
python run.py
```

**Or run directly:**
```bash
streamlit run app.py
```

## Features

- Intelligent responses using Llama3 70B
- Real-time product catalog from S3
- Natural language understanding
- Professional web interface
- 7-second realistic response time
- No fallback mode - requires Bedrock access

## Architecture

- **Frontend:** Streamlit web application
- **LLM:** Amazon Bedrock Llama3 70B Instruct
- **Data:** S3 bucket with product catalogs
- **Search:** AI-powered product matching
- **Deployment:** Cloud-native, scalable

## Requirements

- Python 3.8+
- AWS account with Bedrock access
- S3 bucket for product data
- Internet connection for cloud services
