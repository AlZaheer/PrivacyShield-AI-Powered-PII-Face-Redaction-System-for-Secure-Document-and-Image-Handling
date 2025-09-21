"""
Main Streamlit application for PII and Face De-identification
Author: Senior Python Developer
"""

import streamlit as st
import tempfile
import os
from pathlib import Path
import base64
from io import BytesIO
from PIL import Image

# Import our custom modules
from pii_deidentifier import redact_pii_from_text, get_available_pii_entities
from face_deidentifier import blur_faces_in_image, load_face_detector
from pdf_handler import deidentify_pdf, extract_text_from_pdf, is_pdf_file

# Configure page
st.set_page_config(
    page_title="PII & Face De-identification Tool",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cache the face detector model loading
@st.cache_resource
def load_cached_face_detector():
    """Load and cache the face detection model"""
    return load_face_detector()

# Cache expensive operations
@st.cache_data
def process_image_for_display(image_bytes):
    """Convert image bytes to PIL Image for display"""
    return Image.open(BytesIO(image_bytes))

def create_download_link(file_path, filename, text="Download"):
    """Create a download link for processed files"""
    with open(file_path, "rb") as f:
        bytes_data = f.read()
    b64 = base64.b64encode(bytes_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{text}</a>'
    return href

def main():
    """Main application function"""
    
    # App header
    st.title("🔒 PII & Face De-identification Tool")
    st.markdown("---")
    
    # Sidebar for file upload and options
    with st.sidebar:
        st.header("📁 Upload & Settings")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'jpg', 'jpeg', 'png', 'txt'],
            help="Upload PDF, image, or text files for de-identification"
        )
        
        st.markdown("---")
        
        # De-identification options
        st.header("🛡️ De-identification Options")
        
        redact_pii = st.checkbox(
            "Redact PII",
            value=True,
            help="Remove personally identifiable information from text"
        )
        
        if redact_pii:
            # PII entity selection
            available_entities = get_available_pii_entities()
            selected_entities = st.multiselect(
                "Select PII types to redact:",
                options=available_entities,
                default=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD"],
                help="Choose which types of PII to redact"
            )
        else:
            selected_entities = []
        
        blur_faces = st.checkbox(
            "Blur Faces",
            value=True,
            help="Blur detected faces in images"
        )
        
        st.markdown("---")
        
        # Processing button
        process_button = st.button(
            "🚀 De-identify File",
            disabled=uploaded_file is None or (not redact_pii and not blur_faces),
            help="Start the de-identification process"
        )
    
    # Main content area
    if uploaded_file is None:
        st.info("👆 Please upload a file using the sidebar to get started.")
        
        # Instructions
        with st.expander("📖 How to use this tool"):
            st.markdown("""
            1. **Upload a file**: Choose a PDF, image, or text file from your computer
            2. **Select options**: Choose whether to redact PII, blur faces, or both
            3. **Configure PII types**: If redacting PII, select which types to remove
            4. **Process**: Click the "De-identify File" button
            5. **Download**: Get your processed file with sensitive information removed
            
            **Supported formats:**
            - PDF files (.pdf)
            - Image files (.jpg, .jpeg, .png)
            - Text files (.txt)
            """)
        
        return
    
    # Display file information
    st.header("📄 File Information")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Filename", uploaded_file.name)
    with col2:
        st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
    with col3:
        file_type = "PDF" if uploaded_file.name.lower().endswith('.pdf') else "Text" if uploaded_file.name.lower().endswith('.txt') else "Image"
        st.metric("File Type", file_type)
    
    # Process file when button is clicked
    if process_button:
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Process based on file type
            if is_pdf_file(uploaded_file.name):
                process_pdf_file(tmp_file_path, uploaded_file.name, redact_pii, blur_faces, selected_entities)
            elif uploaded_file.name.lower().endswith('.txt'):
                process_text_file(uploaded_file.getvalue(), uploaded_file.name, redact_pii, selected_entities)
            else:
                process_image_file(uploaded_file.getvalue(), uploaded_file.name, redact_pii, blur_faces, selected_entities)
            
            # Cleanup temporary file
            os.unlink(tmp_file_path)
            
        except Exception as e:
            st.error(f"❌ An error occurred during processing: {str(e)}")
            st.exception(e)

def process_pdf_file(file_path, filename, redact_pii, blur_faces, selected_entities):
    """Process PDF file for de-identification"""
    
    st.header("🔄 Processing PDF...")
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Extract and display original text preview
        status_text.text("Extracting text from PDF...")
        progress_bar.progress(20)
        
        original_text = extract_text_from_pdf(file_path)
        
        if original_text.strip():
            with st.expander("📖 Original Text Preview (first 500 characters)"):
                st.text(original_text[:500] + "..." if len(original_text) > 500 else original_text)
        
        # Process the PDF
        status_text.text("De-identifying PDF content...")
        progress_bar.progress(60)
        
        output_path = deidentify_pdf(
            file_path=file_path,
            redact_pii=redact_pii,
            blur_faces=blur_faces,
            pii_entities=selected_entities if redact_pii else []
        )
        
        progress_bar.progress(100)
        status_text.text("✅ Processing complete!")
        
        # Provide download link
        st.success("🎉 PDF de-identification completed successfully!")
        
        output_filename = f"deidentified_{filename}"
        download_link = create_download_link(output_path, output_filename, "📥 Download De-identified PDF")
        st.markdown(download_link, unsafe_allow_html=True)
        
        # Show processing summary
        st.info(f"""
        **Processing Summary:**
        - PII Redaction: {'✅ Enabled' if redact_pii else '❌ Disabled'}
        - Face Blurring: {'✅ Enabled' if blur_faces else '❌ Disabled'}
        - PII Types: {', '.join(selected_entities) if selected_entities else 'None'}
        """)
        
    except Exception as e:
        error_message = str(e)
        st.error(f"❌ Failed to process PDF: {error_message}")
        
        # Provide specific guidance for common issues
        if "Poppler not installed" in error_message:
            st.warning("""
            **Poppler Installation Required:**
            The PDF processing requires Poppler, which is not installed on your system.
            
            **To fix this issue:**
            1. Download Poppler for Windows from: https://github.com/oschwartz10612/poppler-windows/releases/
            2. Extract the downloaded file to a folder (e.g., `C:\\poppler`)
            3. Add `C:\\poppler\\Library\\bin` to your system PATH environment variable
            4. Restart your terminal/IDE and try again
            
            For detailed instructions, check the `setup_instructions.md` file.
            """)
        elif "Invalid or corrupted PDF file" in error_message:
            st.warning("""
            **Invalid PDF File:**
            The uploaded file appears to be corrupted or is not a valid PDF.
            Please check the file and try uploading again.
            """)
        elif "PDF file not found" in error_message:
            st.warning("""
            **File Access Error:**
            The application cannot access the PDF file. This might be a permission issue.
            Please check that the file exists and you have read permissions.
            """)
        
        raise e

def process_image_file(image_bytes, filename, redact_pii, blur_faces, selected_entities):
    """Process image file for de-identification"""
    
    st.header("🔄 Processing Image...")
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Load original image
        status_text.text("Loading image...")
        progress_bar.progress(20)
        
        original_image = process_image_for_display(image_bytes)
        
        # Process image
        processed_bytes = image_bytes
        
        if blur_faces:
            status_text.text("Detecting and blurring faces...")
            progress_bar.progress(60)
            processed_bytes = blur_faces_in_image(processed_bytes)
        
        progress_bar.progress(100)
        status_text.text("✅ Processing complete!")
        
        # Display results
        st.success("🎉 Image de-identification completed successfully!")
        
        # Before/After comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📷 Original Image")
            st.image(original_image, use_column_width=True)
        
        with col2:
            st.subheader("🔒 De-identified Image")
            processed_image = process_image_for_display(processed_bytes)
            st.image(processed_image, use_column_width=True)
        
        # Download button
        output_filename = f"deidentified_{filename}"
        st.download_button(
            label="📥 Download De-identified Image",
            data=processed_bytes,
            file_name=output_filename,
            mime="image/jpeg"
        )
        
        # Show processing summary
        st.info(f"""
        **Processing Summary:**
        - Face Blurring: {'✅ Enabled' if blur_faces else '❌ Disabled'}
        - Original Size: {original_image.size}
        - Format: {original_image.format}
        """)
        
    except Exception as e:
        st.error(f"❌ Failed to process image: {str(e)}")
        raise e

def process_text_file(text_bytes, filename, redact_pii, selected_entities):
    """Process text file for de-identification"""
    
    st.header("🔄 Processing Text File...")
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Load original text
        status_text.text("Loading text...")
        progress_bar.progress(20)
        
        # Decode bytes to string
        text_content = text_bytes.decode('utf-8')
        
        # Display original text preview
        with st.expander("📖 Original Text Preview (first 1000 characters)"):
            st.text(text_content[:1000] + ("..." if len(text_content) > 1000 else ""))
        
        progress_bar.progress(40)
        status_text.text("Redacting PII from text...")
        
        # Process text
        if redact_pii and selected_entities:
            try:
                processed_text = redact_pii_from_text(text_content, selected_entities)
            except Exception as e:
                st.error(f"Error during PII redaction: {str(e)}")
                raise e
        else:
            processed_text = text_content
        
        progress_bar.progress(80)
        status_text.text("Text processing complete!")
        progress_bar.progress(100)
        
        # Display results
        st.success("🎉 Text de-identification completed successfully!")
        
        # Show before/after comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📄 Original Text")
            st.text_area("Original text", text_content[:2000], height=300, key="original_text")
        
        with col2:
            st.subheader("🔒 De-identified Text")
            st.text_area("De-identified text", processed_text[:2000], height=300, key="processed_text")
        
        # Download button for processed text
        output_filename = f"deidentified_{filename}"
        st.download_button(
            label="📥 Download De-identified Text",
            data=processed_text,
            file_name=output_filename,
            mime="text/plain"
        )
        
        # Show processing summary
        st.info(f"""
        **Processing Summary:**
        - PII Redaction: {'✅ Enabled' if redact_pii else '❌ Disabled'}
        - PII Types: {', '.join(selected_entities) if selected_entities else 'None'}
        """)
        
    except Exception as e:
        st.error(f"❌ Failed to process text file: {str(e)}")
        raise e

if __name__ == "__main__":
    main()
