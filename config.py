import os

S3_URI = os.environ.get("S3_URI", "s3://...../SOP_Document_Control.png" )
AWS_PROFILE_NAME = os.environ.get("AWS_PROFILE_NAME", ".....")
AWS_REGION_NAME = os.environ.get("AWS_REGION_NAME", "us-east-1")
BUCKET_NAME = os.environ.get("BUCKET_NAME", "......")
S3_INPUT_FILE_KEY = os.environ.get("S3_INPUT_FILE_KEY", "SOP/SOP_Document_Control.json")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", ".....") # Your OpenAI API Key
GPT_MODEL = os.environ.get("GPT_MODEL", "gpt-3.5-turbo") # Model to use for OpenAI Chat Completion API