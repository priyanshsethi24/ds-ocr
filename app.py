from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.logs import logger
from routes.ocr_bp import router as pdf_router
from dotenv import load_dotenv
import os
import uvicorn

# Load environment variables from .env file
load_dotenv()

# Access your environment variables
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')
# S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

app = FastAPI()

app.include_router(pdf_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def hello():
    return {"message": "Use /pdf/process endpoint"}

if __name__ == '__main__':
    
    uvicorn.run(app, host='0.0.0.0', port=5000)
    logger.info("Started main.py")
