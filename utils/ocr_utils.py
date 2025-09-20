import os
from pdf2image import convert_from_path
import numpy as np
from config.logs import logger

def extract_text_from_scanned(page, reader, file_path, page_num):
    """
    Extracts text from a scanned page using EasyOCR after converting the page to an image with pdf2image.
    
    Args:
    - page: The page object from the PDF (not used in this function but kept for consistency).
    - reader: The EasyOCR reader instance.
    - file_path (str): Path to the source PDF file.
    - page_num (int): The page number to be processed.

    Returns:
    - str: Extracted text from the scanned page.
    """
    try:
        # Fetch the Poppler path from environment variable
        poppler_path = os.getenv('POPPLER_PATH')
        if not poppler_path:
            error_message = "Poppler path is not set in environment variables."
            logger.error(error_message)
            raise EnvironmentError(error_message)

        logger.info(f"Using Poppler path: {poppler_path}")

        # Convert the specified page to an image
        images = convert_from_path(file_path, first_page=page_num + 1, last_page=page_num + 1, dpi=300, poppler_path=poppler_path)
        image = images[0]  # Get the first (and only) image in the list
        image_np = np.array(image)  # Convert PIL Image to numpy array

        # Use EasyOCR to read text from the image
        result = reader.readtext(image_np)
        
        # Concatenate extracted text from all elements
        return '\n'.join([line[1] for line in result])
    except Exception as e:
        logger.error(f"Failed to extract text from scanned page: {e} [extract_text_from_scanned]")
        raise

