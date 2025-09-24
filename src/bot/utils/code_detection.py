"""
Code Detection Utilities for Discord Bot
Handles text-based and image-based code detection
"""

import re
import io
import logging
import requests
from PIL import Image

logger = logging.getLogger(__name__)

# Try to import OCR functionality
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("pytesseract not available - image detection will be limited")


# Code detection patterns
CODE_PATTERNS = [
    # Programming language keywords and patterns
    r'\b(def|class|import|from|if|else|elif|for|while|try|except|return|function|var|let|const|int|string|bool|float|double|char|void|public|private|protected|static)\b',
    r'[\{\}\[\]();].*[\{\}\[\]();]',  # Multiple brackets/parentheses
    r'#include\s*<.*>',  # C/C++ includes
    r'@\w+',  # Decorators/annotations
    r'\b\w+\s*\(\s*\w*\s*\w+\s*\w*\s*\)',  # Function calls
    r'console\.log|print\(|System\.out|cout\s*<<',  # Output statements
    r'\/\/.*|\/\*.*\*\/|#.*',  # Comments (but be careful with URLs)
    r'\b(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\b',  # SQL keywords
    r'<\/?[a-z][\s\S]*>',  # HTML tags
]

# Compile regex patterns for better performance
compiled_patterns = [re.compile(pattern, re.IGNORECASE | re.MULTILINE) for pattern in CODE_PATTERNS]


class CodeDetector:
    """Handles code detection in text and images"""
    
    def __init__(self, tesseract_available=TESSERACT_AVAILABLE):
        self.tesseract_available = tesseract_available
        
    def detect_code_in_text(self, text):
        """Detect if text contains code using multiple analysis methods"""
        if not text or len(text.strip()) < 10:
            return False
        
        lines = text.split('\n')
        text_lower = text.lower()
        
        # Multi-dimensional analysis
        keyword_score = self._analyze_keywords(text_lower)
        structure_score = self._analyze_structure(lines)
        syntax_score = self._analyze_syntax(text)
        context_score = self._analyze_context(text_lower)
        
        # Calculate weighted total score
        total_score = (
            keyword_score * 0.3 +      # Keywords are important but not definitive
            structure_score * 0.4 +    # Structure is very important for code
            syntax_score * 0.4 +       # Syntax patterns are crucial
            context_score * 0.2        # Context helps reduce false positives
        )
        
        # Debug logging (optional - can be removed in production)
        if total_score > 0.5:  # Only log when close to threshold
            logger.debug(f"Code detection scores: keyword={keyword_score:.2f}, structure={structure_score:.2f}, syntax={syntax_score:.2f}, context={context_score:.2f}, total={total_score:.2f}")
        
        # Threshold for code detection (adjustable)
        return total_score >= 0.6
    
    def _analyze_keywords(self, text_lower):
        """Analyze programming keywords with context awareness"""
        # More specific keyword patterns that are less likely to appear in normal text
        strong_keywords = [
            r'\bdef\s+\w+\s*\(',           # function definitions
            r'\bclass\s+\w+\s*[:\(]',      # class definitions
            r'\bimport\s+\w+',             # import statements
            r'\bfrom\s+\w+\s+import',      # from import statements
            r'\breturn\s+[^;]+[;\n]?',     # return statements
            r'\b(console\.log|print|printf|cout|System\.out)\s*\(',  # output functions
            r'\b(int|string|bool|float|double|char|void)\s+\w+',     # type declarations
            r'\b(public|private|protected|static)\s+',               # access modifiers
        ]
        
        weak_keywords = [
            r'\b(if|else|elif|for|while|try|except|catch)\b',  # Control flow (common in speech)
            r'\b(function|var|let|const)\b',                   # Variable declarations
        ]
        
        strong_matches = 0
        weak_matches = 0
        
        for pattern in strong_keywords:
            if re.search(pattern, text_lower):
                strong_matches += 1
        
        for pattern in weak_keywords:
            matches = len(re.findall(pattern, text_lower))
            weak_matches += matches
        
        # Strong keywords are much more indicative
        keyword_score = (strong_matches * 0.4) + (min(weak_matches, 5) * 0.05)
        return min(keyword_score, 1.0)
    
    def _analyze_structure(self, lines):
        """Analyze code-like structural patterns"""
        if len(lines) < 2:
            return 0
        
        structure_indicators = 0
        indented_lines = 0
        lines_with_endings = 0
        bracket_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            # Check for indentation (common in code)
            if line.startswith((' ', '\t')) and stripped:
                indented_lines += 1
            
            # Check for code-like line endings
            if stripped.endswith((';', '{', '}', ':', ',', ')')):
                lines_with_endings += 1
            
            # Check for brackets/braces
            if any(char in stripped for char in '{}[]()'):
                bracket_lines += 1
        
        total_lines = len([l for l in lines if l.strip()])
        if total_lines == 0:
            return 0
        
        # Calculate structural score
        indentation_ratio = indented_lines / total_lines
        endings_ratio = lines_with_endings / total_lines
        bracket_ratio = bracket_lines / total_lines
        
        structure_score = (indentation_ratio * 0.4 + endings_ratio * 0.4 + bracket_ratio * 0.3)
        return min(structure_score, 1.0)
    
    def _analyze_syntax(self, text):
        """Analyze syntax patterns using compiled regex"""
        matches = 0
        total_patterns = len(compiled_patterns)
        
        for pattern in compiled_patterns:
            if pattern.search(text):
                matches += 1
        
        return matches / total_patterns if total_patterns > 0 else 0
    
    def _analyze_context(self, text_lower):
        """Analyze context to reduce false positives"""
        # Reduce score for conversational indicators
        conversation_indicators = [
            'i think', 'what do you think', 'in my opinion', 'i believe',
            'how are you', 'thanks', 'thank you', 'please help',
            'can you', 'could you', 'would you', 'question about'
        ]
        
        penalty = 0
        for indicator in conversation_indicators:
            if indicator in text_lower:
                penalty += 0.1
        
        return max(0, 0.1 - penalty)  # Small bonus if no conversation indicators
    
    async def detect_code_in_image(self, image_url):
        """Detect code in uploaded image using OCR"""
        if not self.tesseract_available:
            return None  # Indicates OCR unavailable
        
        try:
            # Download image
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Basic size check
            if len(response.content) > 10 * 1024 * 1024:
                logger.warning("Image too large for processing")
                return False
                
            # Convert to PIL Image
            image = Image.open(io.BytesIO(response.content))
            
            # Resize if too large (for faster processing)
            if image.width > 2000 or image.height > 2000:
                image.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
            
            # Extract text using OCR
            extracted_text = pytesseract.image_to_string(image, config='--psm 6')
            
            if not extracted_text.strip():
                logger.debug("No text extracted from image")
                return False
            
            logger.debug(f"Extracted text from image: {extracted_text[:100]}...")
            
            # Check if extracted text contains code
            return self.detect_code_in_text(extracted_text)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error downloading image: {e}")
            return False
        except Exception as e:
            if 'TesseractNotFoundError' in str(type(e)):
                logger.error("Tesseract not found - image detection disabled")
                return None
            logger.error(f"Error processing image: {e}")
            return None
    
    def is_ocr_available(self):
        """Check if OCR functionality is available"""
        return self.tesseract_available