"""
PII De-identification Module
Handles detection and redaction of personally identifiable information using Presidio
"""

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import RecognizerResult, EngineResult
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PIIDeidentifier:
    """Class to handle PII detection and anonymization"""
    
    def __init__(self):
        """Initialize the analyzer and anonymizer engines"""
        try:
            self.analyzer = AnalyzerEngine()
            self.anonymizer = AnonymizerEngine()
            logger.info("PII engines initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PII engines: {e}")
            raise
    
    def analyze_text(self, text, entities=None, language='en'):
        """
        Analyze text for PII entities
        
        Args:
            text (str): Text to analyze
            entities (list): List of entity types to detect
            language (str): Language code
            
        Returns:
            list: List of detected PII entities
        """
        try:
            results = self.analyzer.analyze(
                text=text,
                entities=entities,
                language=language
            )
            return results
        except Exception as e:
            logger.error(f"Failed to analyze text: {e}")
            return []
    
    def anonymize_text(self, text, analyzer_results):
        """
        Anonymize text based on analyzer results
        
        Args:
            text (str): Original text
            analyzer_results (list): Results from analyzer
            
        Returns:
            str: Anonymized text
        """
        try:
            anonymized_result = self.anonymizer.anonymize(
                text=text,
                analyzer_results=analyzer_results
            )
            return anonymized_result.text
        except Exception as e:
            logger.error(f"Failed to anonymize text: {e}")
            return text

# Global instance
_pii_deidentifier = None

def get_pii_deidentifier():
    """Get singleton instance of PII deidentifier"""
    global _pii_deidentifier
    if _pii_deidentifier is None:
        _pii_deidentifier = PIIDeidentifier()
    return _pii_deidentifier

def redact_pii_from_text(text, pii_entities=None):
    """
    Main function to redact PII from text
    
    Args:
        text (str): Input text containing potential PII
        pii_entities (list): List of PII entity types to redact
        
    Returns:
        str: Text with PII redacted
    """
    if not text or not text.strip():
        return text
    
    try:
        deidentifier = get_pii_deidentifier()
        
        # Analyze text for PII
        analyzer_results = deidentifier.analyze_text(text, entities=pii_entities)
        
        if not analyzer_results:
            logger.info("No PII detected in text")
            return text
        
        # Log detected entities (for debugging)
        detected_entities = [result.entity_type for result in analyzer_results]
        logger.info(f"Detected PII entities: {set(detected_entities)}")
        
        # Anonymize the text
        anonymized_text = deidentifier.anonymize_text(text, analyzer_results)
        
        return anonymized_text
        
    except Exception as e:
        logger.error(f"Error in PII redaction: {e}")
        return text  # Return original text if processing fails

def get_available_pii_entities():
    """
    Get list of available PII entity types supported by Presidio
    
    Returns:
        list: List of supported PII entity types
    """
    try:
        deidentifier = get_pii_deidentifier()
        supported_entities = deidentifier.analyzer.get_supported_entities()
        return sorted(supported_entities)
    except Exception as e:
        logger.error(f"Failed to get supported entities: {e}")
        # Return default common entities
        return [
            "PERSON",
            "EMAIL_ADDRESS", 
            "PHONE_NUMBER",
            "CREDIT_CARD",
            "IBAN_CODE",
            "IP_ADDRESS",
            "DATE_TIME",
            "LOCATION",
            "ORGANIZATION",
            "URL",
            "US_SSN",
            "US_DRIVER_LICENSE",
            "US_PASSPORT",
            "MEDICAL_LICENSE",
            "US_BANK_NUMBER"
        ]

def batch_redact_pii(text_list, pii_entities=None):
    """
    Redact PII from multiple text strings
    
    Args:
        text_list (list): List of text strings
        pii_entities (list): List of PII entity types to redact
        
    Returns:
        list: List of texts with PII redacted
    """
    return [redact_pii_from_text(text, pii_entities) for text in text_list]

def get_pii_detection_confidence(text, pii_entities=None):
    """
    Get confidence scores for PII detection
    
    Args:
        text (str): Input text
        pii_entities (list): List of PII entity types to detect
        
    Returns:
        dict: Dictionary with entity types and their confidence scores
    """
    try:
        deidentifier = get_pii_deidentifier()
        analyzer_results = deidentifier.analyze_text(text, entities=pii_entities)
        
        confidence_scores = {}
        for result in analyzer_results:
            entity_type = result.entity_type
            if entity_type not in confidence_scores:
                confidence_scores[entity_type] = []
            confidence_scores[entity_type].append(result.score)
        
        # Calculate average confidence for each entity type
        avg_confidence = {}
        for entity_type, scores in confidence_scores.items():
            avg_confidence[entity_type] = sum(scores) / len(scores)
        
        return avg_confidence
        
    except Exception as e:
        logger.error(f"Error getting PII confidence scores: {e}")
        return {}