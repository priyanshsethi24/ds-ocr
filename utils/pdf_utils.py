import fitz  # PyMuPDF
from config.logs import logger

def is_scanned(page):
    """
    Check if a page is scanned or not by attempting to extract text.

    Args:
    page : Page
        The page object from PyMuPDF to analyze.

    Returns:
    bool
        True if the page is considered scanned, otherwise False.
    """
    try:
        text = page.get_text()
        # A page is considered scanned if less than 50 characters of text are extracted
        is_scanned = len(text.strip()) < 50
        logger.info(str(f"Page scanned status: {'Scanned' if is_scanned else 'Text-based'}")+'[is_scanned] [utils\pdf_utils.py:20]')
        return is_scanned
    except Exception as e:
        logger.error(str("Failed to determine if the page is scanned.")+'[is_scanned] [utils\pdf_utils.py:23]')
        raise

# def create_new_pdf(texts, output_filename):
#     """
#     Create a new PDF with extracted texts.

#     Args:
#     texts : list of str
#         The list of extracted texts to include in the new PDF.
#     output_filename : str
#         The filename for the output PDF.
#     """
#     try:
#         doc = fitz.open()
#         for text in texts:
#             page = doc.new_page()
#             # Insert text into the new page
#             page.insert_text((72, 72), text, fontsize=4, fontname="helv")
#         # Save and close the document
#         doc.save(output_filename)
#         doc.close()
#         logger.info(str(f"New PDF created successfully: {output_filename}")+'[create_new_pdf] [utils\pdf_utils.py:45]')
#     except Exception as e:
#         logger.error(str("Failed to create a new PDF.")+'[create_new_pdf] [utils\pdf_utils.py:47]')
#         raise
