"""
Test script to demonstrate the improved code detection functionality
Run this to see how the detection handles various text samples
"""

import re

class CodeDetectionTester:
    def __init__(self):
        pass
    
    def detect_code_in_text(self, text):
        """Detect if text contains code using multiple sophisticated heuristics"""
        if not text or len(text.strip()) < 15:
            return False
        
        text_lower = text.lower()
        lines = text.split('\n')
        
        # Score different aspects of the text
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
        
        print(f"Text: '{text[:50]}...'")
        print(f"Scores: keyword={keyword_score:.2f}, structure={structure_score:.2f}, syntax={syntax_score:.2f}, context={context_score:.2f}")
        print(f"Total score: {total_score:.2f} - {'CODE DETECTED' if total_score >= 0.6 else 'Normal text'}")
        print("-" * 60)
        
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
            
            # Check for consistent indentation (multiple levels)
            if line.startswith('    ') or line.startswith('\t'):
                indented_lines += 1
            
            # Check for code-like line endings
            if stripped.endswith((';', '{', '}', ':', ',')):
                lines_with_endings += 1
            
            # Check for brackets at end of lines (function calls, array access)
            if re.search(r'[\{\}\[\]()]\s*$', stripped):
                bracket_lines += 1
        
        total_lines = len([l for l in lines if l.strip()])
        
        if total_lines == 0:
            return 0
        
        # Calculate ratios
        indentation_ratio = indented_lines / total_lines
        ending_ratio = lines_with_endings / total_lines
        bracket_ratio = bracket_lines / total_lines
        
        # Multiple lines with indentation is a strong indicator
        if indented_lines >= 3 and indentation_ratio >= 0.5:
            structure_indicators += 0.6
        
        # High ratio of lines ending with code punctuation
        if ending_ratio >= 0.4:
            structure_indicators += 0.4
        
        # Multiple bracket patterns
        if bracket_ratio >= 0.3:
            structure_indicators += 0.3
        
        return min(structure_indicators, 1.0)
    
    def _analyze_syntax(self, text):
        """Analyze syntax patterns specific to code"""
        syntax_score = 0
        
        # Function call patterns (more specific)
        function_calls = len(re.findall(r'\w+\s*\([^)]*\)\s*[;,\n]', text))
        if function_calls >= 2:
            syntax_score += 0.4
        elif function_calls == 1:
            syntax_score += 0.2
        
        # Variable assignment patterns
        assignments = len(re.findall(r'\w+\s*[=]\s*[^=][^;,\n]*[;,\n]', text))
        if assignments >= 2:
            syntax_score += 0.3
        
        # Multiple brackets/parentheses in sequence
        bracket_sequences = len(re.findall(r'[\{\}\[\]()]+', text))
        if bracket_sequences >= 4:
            syntax_score += 0.3
        
        # Comments (but avoid URLs)
        comment_patterns = [
            r'^\s*//[^\n]+$',           # Single line comments
            r'^\s*/\*.*\*/\s*$',        # Block comments
            r'^\s*#(?!http)[^\n]+$',    # Python comments (avoid #hashtags and URLs)
        ]
        
        comments = 0
        for pattern in comment_patterns:
            comments += len(re.findall(pattern, text, re.MULTILINE))
        
        if comments >= 1:
            syntax_score += 0.2
        
        # Code blocks (multiple lines with brackets)
        if re.search(r'\{[^}]*\n[^}]*\}', text, re.DOTALL):
            syntax_score += 0.4
        
        return min(syntax_score, 1.0)
    
    def _analyze_context(self, text_lower):
        """Analyze context to reduce false positives"""
        # Phrases that suggest natural language rather than code
        natural_language_phrases = [
            r'\b(i think|i believe|in my opinion|what if|how about|let me know)\b',
            r'\b(please|thank you|thanks|could you|would you|can you)\b',
            r'\b(the problem is|i need help|i\'m confused|i don\'t understand)\b',
            r'\b(assignment|homework|project|exercise|question)\b',
        ]
        
        # Code-specific phrases that increase confidence
        code_phrases = [
            r'\b(compile|debug|syntax error|runtime error|null pointer)\b',
            r'\b(algorithm|data structure|method|function|variable|array)\b',
            r'\b(loop|iteration|recursion|binary search|sorting)\b',
        ]
        
        natural_count = 0
        code_count = 0
        
        for pattern in natural_language_phrases:
            natural_count += len(re.findall(pattern, text_lower))
        
        for pattern in code_phrases:
            code_count += len(re.findall(pattern, text_lower))
        
        # If lots of natural language indicators, reduce score
        if natural_count >= 3:
            return -0.3
        elif natural_count >= 1:
            return -0.1
        
        # If code-specific terms, increase confidence
        if code_count >= 2:
            return 0.2
        elif code_count >= 1:
            return 0.1
        
        return 0

def test_code_detection():
    """Test the improved code detection with various examples"""
    detector = CodeDetectionTester()
    
    # Test cases
    test_cases = [
        # Should NOT be flagged (natural language)
        "If you want to pass the assignment, else you might fail the class. Please help me understand this problem.",
        
        "What if we try a different approach? I think we should consider all the options before making a decision.",
        
        "The professor said if we don't submit on time, then we get a penalty. I need help with my homework assignment.",
        
        # Should be flagged (actual code)
        """def calculate_grade(score):
    if score >= 90:
        return 'A'
    else:
        return 'B'""",
        
        """for (int i = 0; i < n; i++) {
    console.log(arr[i]);
    sum += arr[i];
}""",
        
        "print('Hello World'); x = 5; y = x * 2;",
        
        """import numpy as np
from sklearn import datasets
data = datasets.load_iris()""",
        
        # Edge cases
        "I'm trying to understand if-else statements in Python programming. Can someone explain the syntax?",
        
        "The function should return true if the condition is met, else it returns false.",
        
        # More code examples that should be detected
        """x = 5;
y = 10;
z = x + y;""",
        
        """public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}""",
        
        "let x = 5; const y = 10; console.log(x + y);",
    ]
    
    print("🧪 Testing Improved Code Detection")
    print("=" * 60)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        detector.detect_code_in_text(test)

if __name__ == "__main__":
    test_code_detection()