# Poppler Installation Guide for Windows

## Why Poppler is Needed
Poppler is a PDF rendering library that is required by the `pdf2image` Python package to convert PDF files to images. Without Poppler installed and properly configured, the PDF processing functionality in this application will fail.

## Installation Steps

### Step 1: Download Poppler
1. Go to the Poppler for Windows releases page: https://github.com/oschwartz10612/poppler-windows/releases/
2. Download the latest release (e.g., `poppler-xx.xx.x_x64.7z` or `poppler-xx.xx.x_x64.zip`)
3. Extract the downloaded file to a folder on your system (e.g., `C:\poppler`)

### Step 2: Add Poppler to System PATH
1. Open the Start Menu and search for "Environment Variables"
2. Click "Edit the system environment variables"
3. In the System Properties window, click the "Environment Variables" button
4. In the "System variables" section, find and select the "Path" variable
5. Click "Edit"
6. Click "New" and add the path to the Poppler bin directory:
   - If you extracted to `C:\poppler`, add: `C:\poppler\Library\bin`
7. Click "OK" to save the changes

### Step 3: Verify Installation
1. Open a new Command Prompt window (important: must be new after changing PATH)
2. Run the following command:
   ```
   pdfinfo -v
   ```
3. If Poppler is correctly installed, you should see version information
4. If you get an error like "'pdfinfo' is not recognized", the PATH was not set correctly

### Step 4: Restart Your Development Environment
1. Close VS Code completely
2. Restart VS Code
3. If you're running the Streamlit app in a terminal, close that terminal and open a new one

## Troubleshooting

### If You Still Get "Poppler not installed" Errors:
1. Make sure you downloaded the correct Poppler package for your system (64-bit or 32-bit)
2. Verify that the PATH includes the correct bin directory
3. Check that you restarted your terminal/IDE after adding to PATH
4. Try running the app from a new terminal window

### Alternative Solution - Specify Poppler Path Directly
If you don't want to modify your system PATH, you can specify the Poppler path directly in the code:

In `pdf_handler.py`, modify the `pdf_to_images` function to include the `poppler_path` parameter:
```python
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
        # Specify the path to your poppler installation
        poppler_path = r"C:\poppler\Library\bin"  # Adjust this path to your poppler installation
        
        # Check if poppler is available by trying a simple conversion
        images = pdf2image.convert_from_path(file_path, dpi=dpi, first_page=1, last_page=1, poppler_path=poppler_path)
        # If that works, convert all pages
        images = pdf2image.convert_from_path(file_path, dpi=dpi, poppler_path=poppler_path)
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
```

## Testing the Installation
After completing the installation, try running the Streamlit app again:
```bash
streamlit run app.py
```

Then upload a PDF file and process it. The error should no longer occur if Poppler is properly installed.
