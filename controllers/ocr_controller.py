from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
import os
import tempfile
from model.main import process_pdf  # Assuming this contains your PDF processing logic
from config.s3_operations import S3Helper  # Ensure this is the correct import path for your S3Helper class
from config.logs import logger

router = APIRouter()

def send_response(data, code):
    """
    Helper function to construct and return a FastAPI JSON response.
    
    Args:
        data (dict): The payload to be returned as JSON.
        code (int): The HTTP status code for the response.
    
    Returns:
        response: A FastAPI JSONResponse object.
    """
    return JSONResponse(content=data, status_code=code)

@router.post('/process')
async def process_pdf_request(request: Request):
    """
    Endpoint to process a PDF file given its S3 path and bucket name.
    
    This function retrieves a PDF file from S3, processes it to extract text using OCR,
    and then either returns the processed file or the original depending on the outcome.
    
    Returns:
        FastAPI JSONResponse: A JSON response containing the outcome of the process or an error message.
    """
    data = await request.json()
    file_path = data.get('file_path')

    if not file_path:
        logger.error("Missing file_path in request [process_pdf_request] [controllers\\ocr_controller.py:37]")
        raise HTTPException(status_code=400, detail="Missing file_path")

    # Normalize the file_path to remove 's3://' prefix and ensure correct bucket handling
    if file_path.startswith('s3://'):
        s3_helper = S3Helper(file_path)
        bucket_name = s3_helper.bucket_name + '/'
        file_path = file_path[len('s3://' + bucket_name):]

    # Extract directory and file information from the path
    dir_path, file_name = os.path.split(file_path)
    file_base, file_ext = os.path.splitext(file_name)

    # Temporary directories for handling files locally
    temp_dir = tempfile.gettempdir()
    local_input_path = os.path.join(temp_dir, file_name)
    local_output_path = os.path.join(temp_dir, f"{file_base}_OCR{file_ext}")

    # Attempt to download the file from S3
    s3_file_path = f"s3://{s3_helper.bucket_name}/{file_path}"
    logger.info(f"Attempting to download file from S3: {s3_file_path} [process_pdf_request]")
    try:
        s3_helper.download_file_from_s3(file_path, local_input_path)
        logger.info(f"File downloaded successfully to {local_input_path} [process_pdf_request]")
    except Exception as e:
        logger.error(f"Failed to download file from S3: {str(e)} at {s3_file_path} [process_pdf_request]")
        raise HTTPException(status_code=500, detail=f"Failed to download file from S3: {str(e)}")

    # Set the model path for OCR processing
    base_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base_directory, 'model')

    # Process the PDF and handle possible failures
    try:
        processed_file_path, ocr_needed = process_pdf(local_input_path, local_output_path, model_path)
        logger.info(f"PDF processed successfully, saved to {processed_file_path} [process_pdf_request]")
    except Exception as e:
        logger.error(f"Failed to process PDF: {str(e)} [process_pdf_request]")
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

    # Upload processed file back to S3 if there were changes
    if processed_file_path and processed_file_path != local_input_path:
        try:
            output_file_path = f"{dir_path}/{file_base}_OCR{file_ext}" if dir_path else f"{file_base}_OCR{file_ext}"
            s3_output_path = f"s3://{s3_helper.bucket_name}/{output_file_path}"
            s3_helper.upload_file_to_s3(processed_file_path, output_file_path)
            logger.info(f"Processed file uploaded successfully to S3 at {s3_output_path} [process_pdf_request]")
            full_s3_output_path = s3_output_path
        except Exception as e:
            logger.error(f"Failed to upload processed file to S3: {str(e)} at {s3_output_path} [process_pdf_request]")
            raise HTTPException(status_code=500, detail=f"Failed to upload processed file to S3: {str(e)}")
    else:
        # If no changes were made, return the original file path
        full_s3_output_path = f"s3://{s3_helper.bucket_name}/{file_path}"

    return send_response({
        'ocr_needed': ocr_needed,
        'output_file': full_s3_output_path
    }, 200)
