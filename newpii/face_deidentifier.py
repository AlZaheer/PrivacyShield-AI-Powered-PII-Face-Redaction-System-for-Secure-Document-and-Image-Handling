"""
Face De-identification Module
Handles face detection and blurring using OpenCV
"""

import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceDeidentifier:
    """Class to handle face detection and blurring"""
    
    def __init__(self):
        """Initialize the face detector"""
        try:
            # Load Haar Cascade classifier for face detection
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Verify classifier loaded correctly
            if self.face_cascade.empty():
                raise Exception("Failed to load Haar Cascade classifier")
            
            logger.info("Face detector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize face detector: {e}")
            raise
    
    def detect_faces(self, image):
        """
        Detect faces in an image
        
        Args:
            image (numpy.ndarray): Input image in BGR format
            
        Returns:
            list: List of face rectangles (x, y, w, h)
        """
        try:
            # Convert to grayscale for detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            return faces
            
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            return []
    
    def blur_face_region(self, image, x, y, w, h, blur_strength=50):
        """
        Apply blur to a specific face region
        
        Args:
            image (numpy.ndarray): Input image
            x, y, w, h (int): Face rectangle coordinates
            blur_strength (int): Strength of blur effect
            
        Returns:
            numpy.ndarray: Image with blurred face region
        """
        try:
            # Extract face region
            face_region = image[y:y+h, x:x+w]
            
            # Apply Gaussian blur
            blurred_face = cv2.GaussianBlur(face_region, (blur_strength, blur_strength), 0)
            
            # Replace the face region with blurred version
            image[y:y+h, x:x+w] = blurred_face
            
            return image
            
        except Exception as e:
            logger.error(f"Error blurring face region: {e}")
            return image
    
    def process_image(self, image_array, blur_strength=50):
        """
        Process image to detect and blur faces
        
        Args:
            image_array (numpy.ndarray): Input image array
            blur_strength (int): Strength of blur effect
            
        Returns:
            numpy.ndarray: Processed image with blurred faces
        """
        try:
            # Make a copy to avoid modifying original
            processed_image = image_array.copy()
            
            # Detect faces
            faces = self.detect_faces(processed_image)
            
            logger.info(f"Detected {len(faces)} face(s)")
            
            # Blur each detected face
            for (x, y, w, h) in faces:
                processed_image = self.blur_face_region(
                    processed_image, x, y, w, h, blur_strength
                )
            
            return processed_image
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return image_array

# Global instance
_face_deidentifier = None

def load_face_detector():
    """Load and return face detector instance"""
    global _face_deidentifier
    if _face_deidentifier is None:
        _face_deidentifier = FaceDeidentifier()
    return _face_deidentifier

def blur_faces_in_image(image_bytes, blur_strength=50):
    """
    Main function to blur faces in image from bytes
    
    Args:
        image_bytes (bytes): Image data as bytes
        blur_strength (int): Strength of blur effect (must be odd number)
        
    Returns:
        bytes: Processed image as bytes with blurred faces
    """
    try:
        # Ensure blur strength is odd (required for Gaussian blur)
        if blur_strength % 2 == 0:
            blur_strength += 1
        
        # Convert bytes to PIL Image
        pil_image = Image.open(BytesIO(image_bytes))
        
        # Convert PIL to OpenCV format (BGR)
        opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        # Load face detector
        detector = load_face_detector()
        
        # Process image to blur faces
        processed_image = detector.process_image(opencv_image, blur_strength)
        
        # Convert back to PIL Image (RGB)
        processed_pil = Image.fromarray(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
        
        # Convert to bytes
        output_buffer = BytesIO()
        processed_pil.save(output_buffer, format='JPEG', quality=95)
        output_bytes = output_buffer.getvalue()
        
        return output_bytes
        
    except Exception as e:
        logger.error(f"Error in blur_faces_in_image: {e}")
        return image_bytes  # Return original if processing fails

def get_face_detection_stats(image_bytes):
    """
    Get statistics about face detection in an image
    
    Args:
        image_bytes (bytes): Image data as bytes
        
    Returns:
        dict: Statistics including number of faces, confidence scores, etc.
    """
    try:
        # Convert bytes to OpenCV format
        pil_image = Image.open(BytesIO(image_bytes))
        opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        # Load face detector
        detector = load_face_detector()
        
        # Detect faces
        faces = detector.detect_faces(opencv_image)
        
        stats = {
            'num_faces': len(faces),
            'face_regions': faces.tolist() if len(faces) > 0 else [],
            'image_size': opencv_image.shape[:2],  # (height, width)
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting face detection stats: {e}")
        return {'num_faces': 0, 'face_regions': [], 'image_size': (0, 0)}

def create_face_preview(image_bytes, show_rectangles=True):
    """
    Create preview image showing detected faces with rectangles
    
    Args:
        image_bytes (bytes): Image data as bytes
        show_rectangles (bool): Whether to draw rectangles around faces
        
    Returns:
        bytes: Preview image with face detection rectangles
    """
    try:
        # Convert bytes to OpenCV format
        pil_image = Image.open(BytesIO(image_bytes))
        opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        # Load face detector
        detector = load_face_detector()
        
        # Detect faces
        faces = detector.detect_faces(opencv_image)
        
        if show_rectangles and len(faces) > 0:
            # Draw rectangles around detected faces
            for (x, y, w, h) in faces:
                cv2.rectangle(opencv_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(opencv_image, 'Face', (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Convert back to PIL and bytes
        processed_pil = Image.fromarray(cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB))
        output_buffer = BytesIO()
        processed_pil.save(output_buffer, format='JPEG', quality=95)
        
        return output_buffer.getvalue()
        
    except Exception as e:
        logger.error(f"Error creating face preview: {e}")
        return image_bytes