# PII & Face De-identification Tool

A comprehensive Streamlit application for de-identifying personally identifiable information (PII) and faces in uploaded PDF and image files.

## Features

- **PII Redaction**: Automatically detect and redact various types of PII including:
  - Names (PERSON)
  - Email addresses
  - Phone numbers
  - Credit card numbers
  - SSNs and other sensitive identifiers

- **Face Blurring**: Automatically detect and blur faces in images and PDF documents

- **Multiple File Formats**: Support for PDF, JPG, JPEG, and PNG files

- **Modular Architecture**: Clean, maintainable code structure with separate modules for different functionalities

- **User-Friendly Interface**: Intuitive Streamlit interface with progress tracking and before/after comparisons

## Installation

1. **Clone or download the project files**

2. **Install system dependencies** (required for PDF processing):
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install poppler-utils tesseract-ocr
   
   # macOS (using Homebrew)
   brew install poppler tesseract
   
   # Windows: Download and install from official sources
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download the spaCy language model**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

## Usage

1. **Start the application**:
   ```bash
   streamlit run app.py
   ```

2. **Upload a file**: Use the sidebar to upload a PDF or image file

3. **Configure options**:
   - Check "Redact PII" to remove personally identifiable information
   - Select specific PII types to redact
   - Check "Blur Faces" to blur detected faces

4. **Process the file**: Click "De-identify File" to start processing

5. **Download results**: Download the processed file with sensitive information removed

## Project Structure

```
├── app.py                 # Main Streamlit application
├── pii_deidentifier.py    # PII detection and redaction module
├── face_deidentifier.py   # Face detection and blurring module
├── pdf_handler.py         # PDF processing and manipulation module
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Module Details

### `pii_deidentifier.py`
- Uses Microsoft Presidio for PII detection and anonymization
- Supports multiple entity types with configurable confidence thresholds
- Provides batch processing capabilities

### `face_deidentifier.py`
- Uses OpenCV with Haar Cascade classifiers for face detection
- Applies Gaussian blur to detected face regions
- Provides face detection statistics and preview functionality

### `pdf_handler.py`
- Handles PDF text extraction using PyMuPDF
- Converts PDFs to images for processing
- Reconstructs PDFs with de-identified content
- Manages temporary files and cleanup

### `app.py`
- Streamlit interface with clean, intuitive design
- Progress tracking and error handling
- Before/after comparisons for processed content
- Caching for performance optimization

## Configuration

The application uses sensible defaults but can be customized:

- **PII Entity Types**: Select which types of PII to detect and redact
- **Face Blur Strength**: Adjust the intensity of face blurring
- **Processing Quality**: Configure image resolution and quality settings

## Security Considerations

- Temporary files are automatically cleaned up after processing
- Original files are never modified - only copies are processed
- All processing happens locally - no data is sent to external services
- Secure file handling with proper validation

## Performance Optimization

- Model loading is cached using Streamlit's `@st.cache_resource`
- Image processing operations are optimized for memory usage
- Batch processing support for multiple files
- Progress tracking for long-running operations

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure all dependencies are installed correctly
2. **Model loading failures**: Download the required spaCy model
3. **PDF processing errors**: Install system dependencies (poppler-utils)
4. **Memory issues**: Process smaller files or reduce image resolution

### System Requirements

- Python 3.8 or higher
- At least 4GB RAM for processing large PDFs
- Sufficient disk space for temporary files

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Support

For support and questions, please open an issue in the project repository.