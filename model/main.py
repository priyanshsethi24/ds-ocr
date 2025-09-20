import fitz  # PyMuPDF, a Python library for PDF manipulation
import ocrmypdf  # Tesseract-based OCR library for PDFs
from utils.pdf_utils import is_scanned
import os
from config.logs import logger
from pikepdf import Pdf, Page

def process_pdf(file_path, output_filename, model_path=None):
    """
    Processes a PDF file to extract text from scanned pages using OCR,
    and generates a new PDF with the extracted text if needed. Digital pages are copied unchanged.
    Bookmarks are preserved.
    
    Args:
    - file_path (str): Path to the source PDF file.
    - output_filename (str): Name of the output PDF file.
    - model_path (str, optional): Not used in this version, retained for compatibility.

    Returns:
    - tuple: A tuple containing the path to the output PDF file and an OCR flag (1 if OCR was needed, 0 otherwise).
    """
    ocr_needed = 0
    temp_output_filename = f"{os.path.splitext(output_filename)[0]}_temp.pdf"

    try:
        doc = fitz.open(file_path)
        src_pdf = Pdf.open(file_path)
        output_pdf = Pdf.new()

        # Extract and preserve the bookmarks
        bookmarks = extract_bookmarks(doc)

        for page_num, page in enumerate(doc):
            if is_scanned(page):
                ocr_needed = 1
                logger.info(
                    str(f"Page {page_num + 1} is scanned. Extracting text with OCR...") + '[process_pdf] [model\\main.py:39]')
                
                temp_page_output_filename = f"{os.path.splitext(output_filename)[0]}_temp_page_{page_num + 1}.pdf"
                ocr_single_page(file_path, temp_page_output_filename, page_num)

                temp_doc = Pdf.open(temp_page_output_filename)
                output_pdf.pages.append(temp_doc.pages[0])
                temp_doc.close()
                os.remove(temp_page_output_filename)
            else:
                # Ensure digital pages are always copied over to the new document
                logger.info(
                    str(f"Page {page_num + 1} is digital. Adding page unchanged...") + '[process_pdf] [model\\main.py:49]')
                output_pdf.pages.append(src_pdf.pages[page_num])

        # Save the output document only if OCR was needed
        if ocr_needed and len(output_pdf.pages) > 0:
            output_pdf.save(temp_output_filename)
            temp_output_filename = os.path.abspath(temp_output_filename)  # Get the absolute path to return

            # Add bookmarks to the new document
            with fitz.open(temp_output_filename) as new_doc:
                add_bookmarks(new_doc, bookmarks)
                new_doc.save(output_filename)
        else:
            output_filename = None  # No output file generated if no OCR was needed

    except Exception as e:
        logger.error(str(f"An error occurred while processing the PDF: {e}") + '[process_pdf] [model\\main.py:67]')
        raise
    finally:
        if doc:
            doc.close()

    return output_filename, ocr_needed


def ocr_single_page(file_path, save_path, page_num):
    """
    Runs OCR on a single page of a PDF using ocrmypdf.

    Args:
    - file_path (str): Path to the source PDF file.
    - save_path (str): Path to save the OCR-processed page as a PDF.
    - page_num (int): The zero-based index of the page to process.

    Returns:
    - None
    """
    try:
        # Extract the single page using PyMuPDF
        doc = fitz.open(file_path)
        single_page_doc = fitz.open()  # Create a new PDF
        single_page_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

        temp_file = f"{os.path.splitext(save_path)[0]}_single_page.pdf"
        single_page_doc.save(temp_file)
        single_page_doc.close()
        doc.close()

        ocrmypdf.ocr(temp_file, save_path, skip_text=True)
        os.remove(temp_file)
    except Exception as e:
        logger.error(str(f"An error occurred during OCR processing: {e}") + '[ocr_single_page] [model\\main.py]')
        raise

def extract_bookmarks(doc):
    """
    Extracts bookmarks from a PyMuPDF document.

    Args:
    - doc (fitz.Document): The PyMuPDF document.

    Returns:
    - list: A list of bookmarks.
    """
    bookmarks = []
    toc = doc.get_toc()
    for entry in toc:
        bookmarks.append(entry)
    return bookmarks

def add_bookmarks(doc, bookmarks):
    """
    Adds bookmarks to a PyMuPDF document.

    Args:
    - doc (fitz.Document): The PyMuPDF document.
    - bookmarks (list): A list of bookmarks to add.

    Returns:
    - None
    """
    doc.set_toc(bookmarks)
