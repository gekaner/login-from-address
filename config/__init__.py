from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_GPT = os.getenv('api-gpt')

DADATA_TOKEN = os.getenv('DADATA_TOKEN')

PROXY = os.getenv('proxy')

HTTP_REDIS = os.getenv('HTTP_REDIS')
HTTP_VECTOR = os.getenv('HTTP_VECTOR')

TIMEOUT = 30