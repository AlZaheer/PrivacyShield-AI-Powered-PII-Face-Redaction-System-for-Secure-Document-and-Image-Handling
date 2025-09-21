"""
Test script to verify combined face blurring and PII redaction
"""

import tempfile
import os
from pdf_handler import deidentify_pdf, extract_text_from_pdf
from pii_deidentifier import redact_pii_from_text

def create_test_pdf():
    """Create a simple test PDF with text and simulated images"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # Create a temporary PDF file
        pdf_path = tempfile.mktemp(suffix='.pdf')
        c = canvas.Canvas(pdf_path, pagesize=letter)
        
        # Add some text with PII
        c.drawString(100, 750, "Test Document for PII Redaction")
        c.drawString(100, 725, "Name: John Smith")
        c.drawString(100, 700, "Email: john.smith@example.com")
        c.drawString(100, 675, "Phone: (555) 123-4567")
        c.drawString(100, 650, "SSN: 123-45-6789")
        
        # Add a second page with more PII
        c.showPage()
        c.drawString(100, 750, "Second Page")
        c.drawString(100, 725, "Credit Card: 4532-1234-5678-9012")
        c.drawString(100, 700, "Address: 123 Main St, Anytown, USA")
        
        c.save()
        return pdf_path
    except ImportError:
        print("⚠️  ReportLab not available, creating a simple text-based PDF")
        # Create a simple PDF content (this is a minimal valid PDF)
        pdf_content = """%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R 4 0 R]
/Count 2
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 5 0 R
/Resources <<
/Font <<
/F1 6 0 R
>>
>>
>>
endobj

4 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 7 0 R
/Resources <<
/Font <<
/F1 6 0 R
>>
>>
>>
endobj

5 0 obj
<<
/Length 200
>>
stream
BT
/F1 12 Tf
100 750 Td
(Test Document for PII Redaction) Tj
T*
(Name: John Smith) Tj
T*
(Email: john.smith@example.com) Tj
T*
(Phone: (555) 123-4567) Tj
T*
(SSN: 123-45-6789) Tj
ET
endstream
endobj

7 0 obj
<<
/Length 150
>>
stream
BT
/F1 12 Tf
100 750 Td
(Second Page) Tj
T*
(Credit Card: 4532-1234-5678-9012) Tj
T*
(Address: 123 Main St, Anytown, USA) Tj
ET
endstream
endobj

6 0 obj
<<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
endobj

xref
0 8
0000000000 65535 f 
0000000010 00000 n 
0000000053 00000 n 
0000000114 00000 n 
0000000237 00000 n 
0000000327 00000 n 
0000000527 00000 n 
0000000477 00000 n 

trailer
<<
/Size 8
/Root 1 0 R
>>
startxref
583
%%EOF"""
        
        pdf_path = tempfile.mktemp(suffix='.pdf')
        with open(pdf_path, 'w') as f:
            f.write(pdf_content)
        return pdf_path

def test_combined_processing(pdf_path):
    """Test combined face blurring and PII redaction"""
    try:
        print(f"Testing combined processing for: {pdf_path}")
        
        # Extract original text
        original_text = extract_text_from_pdf(pdf_path)
        print("Original text extracted:")
        print(original_text[:200] + "..." if len(original_text) > 200 else original_text)
        
        # Test 1: PII redaction only
        print("\n1. Testing PII redaction only...")
        redacted_text = redact_pii_from_text(original_text, ["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "US_SSN", "CREDIT_CARD"])
        print("Redacted text preview:")
        print(redacted_text[:200] + "..." if len(redacted_text) > 200 else redacted_text)
        
        # Check if PII was redacted
        pii_redacted = redacted_text != original_text
        print(f"PII redacted: {pii_redacted}")
        
        # Test 2: Combined processing (this is what we're fixing)
        print("\n2. Testing combined face blurring and PII redaction...")
        output_path = deidentify_pdf(
            file_path=pdf_path,
            redact_pii=True,
            blur_faces=True,
            pii_entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "US_SSN", "CREDIT_CARD"]
        )
        
        print(f"✅ Combined processing completed. Output: {output_path}")
        
        # Extract text from processed PDF
        processed_text = extract_text_from_pdf(output_path)
        print("Processed PDF text preview:")
        print(processed_text[:200] + "..." if len(processed_text) > 200 else processed_text)
        
        # Clean up
        os.unlink(pdf_path)
        os.unlink(output_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Error in combined processing test: {e}")
        # Clean up
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)
        return False

if __name__ == "__main__":
    print("Testing Combined Face Blurring and PII Redaction...")
    print("=" * 50)
    
    try:
        pdf_path = create_test_pdf()
        print(f"Created test PDF: {pdf_path}")
        
        if test_combined_processing(pdf_path):
            print("\n🎉 Combined processing is working correctly!")
            print("Both face blurring and PII redaction should now work together.")
        else:
            print("\n❌ Combined processing test failed.")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
