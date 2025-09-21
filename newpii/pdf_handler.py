"""
PDF Processing Module
Handles PDF parsing, text extraction, image extraction, and creation of de-identified PDFs
"""

import PyPDF2
import pdf2image
import fitz  # PyMuPDF
from PIL import Image
import io
import os
import tempfile
from pathlib import Path
import logging

# Import our custom modules
from pii_deidentifier import redact_pii_from_text
from face_deidentifier import blur_faces_in_image

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFHandler:
    """Class to handle PDF processing operations"""
    
    def __init__(self):
        """Initialize PDF handler"""
        self.temp_files = []  # Track temporary files for cleanup
    
    def __del__(self):
        """Cleanup temporary files"""
        self.cleanup_temp_files()
    
    def cleanup_temp_files(self):
        """Remove temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {temp_file}: {e}")
        self.temp_files.clear()
    
    def extract_text_from_pdf(self, file_path):
        """
        Extract text from PDF file
        
        Args:
            file_path (str): Path to PDF file
            
        Returns:
            str: Extracted text from all pages
        """
        try:
            text_content = ""
            
            # Use PyMuPDF for better text extraction
            with fitz.open(file_path) as doc:
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text_content += page.get_text()
                    text_content += "\n\n"  # Separate pages
            
            return text_content
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""
    
    def extract_images_from_pdf(self, file_path):
        """
        Extract images from PDF file
        
        Args:
            file_path (str): Path to PDF file
            
        Returns:
            list: List of image data (as bytes) extracted from PDF
        """
        try:
            images = []
            
            with fitz.open(file_path) as doc:
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    image_list = page.get_images()
                    
                    for img_index, img in enumerate(image_list):
                        # Get image data
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        if pix.n - pix.alpha < 4:  # GRAY or RGB
                            img_data = pix.tobytes("png")
                            images.append({
                                'data': img_data,
                                'page': page_num,
                                'index': img_index,
                                'xref': xref
                            })
                        
                        pix = None  # Release memory
            
            logger.info(f"Extracted {len(images)} images from PDF")
            return images
            
        except Exception as e:
            logger.error(f"Error extracting images from PDF: {e}")
            return []
    
    def create_deidentified_pdf(self, original_path, output_path, redacted_text=None, processed_images=None):
        """
        Create a new PDF with de-identified content
        
        Args:
            original_path (str): Path to original PDF
            output_path (str): Path for output PDF
            redacted_text (str): Text with PII redacted
            processed_images (list): List of processed images
            
        Returns:
            str: Path to created PDF
        """
        try:
            # Open original PDF
            original_doc = fitz.open(original_path)
            new_doc = fitz.open()  # New empty document
            
            for page_num in range(len(original_doc)):
                # Get original page
                original_page = original_doc.load_page(page_num)
                
                # Create new page with same dimensions
                new_page = new_doc.new_page(
                    width=original_page.rect.width,
                    height=original_page.rect.height
                )
                
                # If we have redacted text, replace text content
                if redacted_text:
                    # Get page-specific text (approximate)
                    page_text = original_page.get_text()
                    if page_text.strip():
                        # Insert redacted text (simplified approach)
                        # In a real implementation, you'd want to preserve formatting
                        text_rect = fitz.Rect(50, 50, original_page.rect.width - 50, original_page.rect.height - 50)
                        new_page.insert_textbox(text_rect, redacted_text, fontsize=12)
                else:
                    # Copy original content if no text redaction
                    new_page.show_pdf_page(original_page.rect, original_doc, page_num)
                
                # Handle images
                if processed_images:
                    # Replace images with processed versions
                    # This is a complex operation that would require detailed image positioning
                    pass
            
            # Save new PDF
            new_doc.save(output_path)
            new_doc.close()
            original_doc.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating de-identified PDF: {e}")
            raise
    
    def pdf_to_images(self, file_path, dpi=200):
        """
        Convert PDF pages to images
        
        Args:
            file_path (str): Path to PDF file
            dpi (int): Resolution for conversion
            
        Returns:
            list: List of PIL Images for each page
        """
        try:
            # Check if poppler is available by trying a simple conversion
            images = pdf2image.convert_from_path(file_path, dpi=dpi, first_page=1, last_page=1)
            # If that works, convert all pages
            images = pdf2image.convert_from_path(file_path, dpi=dpi)
            logger.info(f"Converted PDF to {len(images)} page images")
            return images
        except pdf2image.pdf2image.PDFPopplerNotInstalledError as e:
            logger.error(f"Poppler not installed or not in PATH: {e}")
            raise Exception("Poppler not installed. Please install Poppler and add it to your system PATH.")
        except pdf2image.pdf2image.PDFPageCountError as e:
            logger.error(f"Invalid or corrupted PDF file: {e}")
            raise Exception("Invalid or corrupted PDF file. Please check the file and try again.")
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            # Check if it's a path issue
            import os
            if not os.path.exists(file_path):
                raise Exception(f"PDF file not found: {file_path}")
            # Check if it's a permission issue
            if not os.access(file_path, os.R_OK):
                raise Exception(f"Permission denied accessing PDF file: {file_path}")
            # Generic error with more details
            raise Exception(f"Failed to convert PDF to images. This may be due to missing system dependencies (Poppler). Error: {str(e)}")
    
    def images_to_pdf(self, images, output_path):
        """
        Convert list of images to PDF
        
        Args:
            images (list): List of PIL Images
            output_path (str): Path for output PDF
            
        Returns:
            str: Path to created PDF
        """
        try:
            if not images:
                raise ValueError("No images provided")
            
            # Convert all images to RGB if they aren't already
            rgb_images = []
            for img in images:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                rgb_images.append(img)
            
            # Save as PDF
            rgb_images[0].save(
                output_path,
                save_all=True,
                append_images=rgb_images[1:],
                format='PDF'
            )
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error converting images to PDF: {e}")
            raise

    def deidentify_pdf(self, file_path, redact_pii=True, blur_faces=True, pii_entities=None):
        """
        Main function to de-identify a PDF file
        
        Args:
            file_path (str): Path to input PDF file
            redact_pii (bool): Whether to redact PII from text
            blur_faces (bool): Whether to blur faces in images
            pii_entities (list): List of PII entity types to redact
            
        Returns:
            str: Path to de-identified PDF file
        """
        try:
            # Create output path
            output_dir = tempfile.gettempdir()
            base_name = Path(file_path).stem
            output_path = os.path.join(output_dir, f"deidentified_{base_name}.pdf")
            
            # Open the original PDF document
            doc = fitz.open(file_path)
            
            # Extract text for PII analysis
            original_text = self.extract_text_from_pdf(file_path)
            
            # Redact PII if requested
            if redact_pii:
                redacted_text = redact_pii_from_text(original_text, pii_entities)
                logger.info("PII redaction completed")
                
                # Analyze text to find PII positions for redaction
                from pii_deidentifier import get_pii_deidentifier
                deidentifier = get_pii_deidentifier()
                analyzer_results = deidentifier.analyze_text(original_text, entities=pii_entities)
            else:
                analyzer_results = []
            
            # Process each page
            for page_num in range(len(doc)):
                logger.info(f"Processing page {page_num + 1}/{len(doc)}")
                
                # Get the page
                page = doc[page_num]
                
                # Redact PII text on this page
                if redact_pii and analyzer_results:
                    # Find and redact PII entities on this page
                    page_text = page.get_text()
                    page_start = 0
                    if page_num > 0:
                        # Calculate start position of this page's text in the full document text
                        for i in range(page_num):
                            prev_page = doc[i]
                            page_start += len(prev_page.get_text()) + 2  # +2 for \n\n
                    
                    # Process each PII entity
                    for result in analyzer_results:
                        # Check if this entity is on the current page
                        if page_start <= result.start <= page_start + len(page_text):
                            # Adjust positions to be relative to this page
                            page_relative_start = result.start - page_start
                            page_relative_end = result.end - page_start
                            
                            # Get the text that needs to be redacted
                            text_to_redact = page_text[page_relative_start:page_relative_end]
                            
                            # Search for this text on the page
                            text_instances = page.search_for(text_to_redact)
                            
                            # Add redaction annotation for each instance
                            for rect in text_instances:
                                page.add_redact_annot(rect, text="[REDACTED]")
                    
                    # Apply redactions
                    page.apply_redactions()
                
                # Blur faces in images on this page
                if blur_faces:
                    # Get list of images on this page
                    image_list = page.get_images()
                    
                    # Process each image
                    for img_index, img in enumerate(image_list):
                        # Get image data
                        xref = img[0]
                        try:
                            pix = fitz.Pixmap(doc, xref)
                            
                            # Convert to RGB if needed
                            if pix.n - pix.alpha < 4:  # GRAY or RGB
                                img_data = pix.tobytes("png")
                                
                                # Blur faces in the image
                                blurred_img_bytes = blur_faces_in_image(img_data)
                                
                            # Replace the original image with the blurred one
                            # Properly replace image stream in PyMuPDF
                            # Delete old image xref
                            doc._deleteObject(xref)
                            # Insert new image
                            img_rects = page.get_image_rects(xref)
                            if img_rects:
                                rect = img_rects[0]
                                # Insert new image at the same position
                                new_xref = doc.insert_image(rect, stream=blurred_img_bytes)
                                # Replace image reference in page contents
                                # This is complex; alternatively, we can overlay the blurred image
                                page.insert_image(rect, stream=blurred_img_bytes)
                            else:
                                # Fallback: insert image at top-left corner
                                page.insert_image(fitz.Rect(0, 0, 100, 100), stream=blurred_img_bytes)
                        
                            # Clean up
                            pix = None
                        except Exception as img_error:
                            logger.warning(f"Failed to process image {img_index} on page {page_num}: {img_error}")
            
            # Save the modified document
            doc.save(output_path, garbage=4, deflate=True)
            doc.close()
            
            return output_path
                
        except Exception as e:
            logger.error(f"Error in deidentify_pdf: {e}")
            # Clean up in case of error
            if 'doc' in locals():
                try:
                    doc.close()
                except:
                    pass
            raise

# Global instance
_pdf_handler = None

def get_pdf_handler():
    """Get singleton instance of PDF handler"""
    global _pdf_handler
    if _pdf_handler is None:
        _pdf_handler = PDFHandler()
    return _pdf_handler

def is_pdf_file(filename):
    """Check if file is a PDF"""
    return filename.lower().endswith('.pdf')

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    handler = get_pdf_handler()
    return handler.extract_text_from_pdf(file_path)

def get_pdf_info(file_path):
    """
    Get information about a PDF file
    
    Args:
        file_path (str): Path to PDF file
        
    Returns:
        dict: Information about the PDF
    """
    try:
        with fitz.open(file_path) as doc:
            info = {
                'page_count': len(doc),
                'title': doc.metadata.get('title', ''),
                'author': doc.metadata.get('author', ''),
                'subject': doc.metadata.get('subject', ''),
                'creator': doc.metadata.get('creator', ''),
                'producer': doc.metadata.get('producer', ''),
                'creation_date': doc.metadata.get('creationDate', ''),
                'modification_date': doc.metadata.get('modDate', ''),
                'has_text': False,
                'has_images': False
            }
            
            # Check if PDF has text content
            total_text = ""
            total_images = 0
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text().strip()
                total_text += page_text
                
                # Count images
                total_images += len(page.get_images())
            
            info['has_text'] = bool(total_text.strip())
            info['has_images'] = total_images > 0
            info['text_length'] = len(total_text)
            info['image_count'] = total_images
            
            return info
            
    except Exception as e:
        logger.error(f"Error getting PDF info: {e}")
        return {}

def deidentify_pdf(file_path, redact_pii=True, blur_faces=True, pii_entities=None):
    """
    Main function to de-identify a PDF file (module-level wrapper)
    
    Args:
        file_path (str): Path to input PDF file
        redact_pii (bool): Whether to redact PII from text
        blur_faces (bool): Whether to blur faces in images
        pii_entities (list): List of PII entity types to redact
        
    Returns:
        str: Path to de-identified PDF file
    """
    handler = get_pdf_handler()
    return handler.deidentify_pdf(file_path, redact_pii, blur_faces, pii_entities)
