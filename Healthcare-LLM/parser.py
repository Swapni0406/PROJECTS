import io
from typing import Optional
import PyPDF2
from PIL import Image
import pytesseract


class ReportParser:
    """Parse medical reports from various formats"""
    
    def extract_text(self, content: bytes, content_type: str) -> str:
        """
        Extract text from uploaded file
        
        Args:
            content: File content as bytes
            content_type: MIME type of the file
        
        Returns:
            Extracted text
        """
        if content_type == "application/pdf":
            return self._extract_from_pdf(content)
        elif content_type == "text/plain":
            return content.decode("utf-8")
        elif content_type in ["image/png", "image/jpeg"]:
            return self._extract_from_image(content)
        else:
            raise ValueError(f"Unsupported content type: {content_type}")
    
    def _extract_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF"""
        text = ""
        pdf_file = io.BytesIO(content)
        
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            raise ValueError(f"Error parsing PDF: {str(e)}")
        
        return text.strip()
    
    def _extract_from_image(self, content: bytes) -> str:
        """Extract text from image using OCR"""
        try:
            image = Image.open(io.BytesIO(content))
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            raise ValueError(f"Error performing OCR: {str(e)}")
    
    def identify_report_type(self, text: str) -> str:
        """
        Identify the type of medical report
        
        Args:
            text: Extracted text
        
        Returns:
            Report type (e.g., "blood_test", "lipid_panel", "metabolic_panel")
        """
        text_lower = text.lower()
        
        # Common report types
        if any(term in text_lower for term in ["cholesterol", "hdl", "ldl", "triglycerides"]):
            return "lipid_panel"
        elif any(term in text_lower for term in ["glucose", "sodium", "potassium", "creatinine"]):
            return "metabolic_panel"
        elif any(term in text_lower for term in ["tsh", "t3", "t4", "thyroid"]):
            return "thyroid_function"
        elif any(term in text_lower for term in ["hemoglobin", "wbc", "rbc", "platelet"]):
            return "complete_blood_count"
        else:
            return "general_health_report"
    
    def extract_key_values(self, text: str) -> dict:
        """
        Extract key-value pairs from report text
        
        Args:
            text: Report text
        
        Returns:
            Dictionary of extracted values
        """
        # This is a simplified implementation
        # In production, you'd use more sophisticated NER (Named Entity Recognition)
        import re
        
        values = {}
        lines = text.split('\n')
        
        for line in lines:
            # Look for patterns like "Test Name: Value Unit"
            match = re.search(r'([A-Za-z\s]+):\s*(\d+\.?\d*)\s*([A-Za-z/]+)?', line)
            if match:
                name, value, unit = match.groups()
                values[name.strip()] = {
                    "value": value,
                    "unit": unit if unit else None
                }
        
        return values
