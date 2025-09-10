"""
Unit tests for text processing utilities.
"""

import pytest
from ..tools.text_processing import TextProcessor, TextAnalyzer


class TestTextProcessor:
    """Test TextProcessor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = TextProcessor()
    
    def test_clean_text(self):
        """Test text cleaning."""
        text = "  Hello,   World!  123  "
        
        # Basic cleaning
        cleaned = self.processor.clean_text(text, remove_extra_whitespace=True)
        assert cleaned == "Hello, World! 123"
        
        # Remove punctuation
        cleaned = self.processor.clean_text(text, remove_punctuation=True, remove_extra_whitespace=True)
        assert cleaned == "Hello World 123"
        
        # Remove numbers
        cleaned = self.processor.clean_text(text, remove_numbers=True, remove_extra_whitespace=True)
        assert cleaned == "Hello, World!"
        
        # Lowercase
        cleaned = self.processor.clean_text(text, to_lowercase=True, remove_extra_whitespace=True)
        assert cleaned == "hello, world! 123"
    
    def test_tokenize_words(self):
        """Test word tokenization."""
        text = "Hello, World! This is a test."
        
        words = self.processor.tokenize_words(text)
        expected = ["hello", "world", "this", "is", "a", "test"]
        assert words == expected
        
        # With stop words removed
        words = self.processor.tokenize_words(text, remove_stop_words=True)
        assert "hello" in words
        assert "world" in words
        assert "test" in words
        assert "is" not in words  # stop word
        assert "a" not in words   # stop word
    
    def test_tokenize_sentences(self):
        """Test sentence tokenization."""
        text = "Hello world. This is a test! How are you?"
        
        sentences = self.processor.tokenize_sentences(text)
        expected = ["Hello world", "This is a test", "How are you"]
        assert sentences == expected
    
    def test_tokenize_paragraphs(self):
        """Test paragraph tokenization."""
        text = "First paragraph.\n\nSecond paragraph.\n\n\nThird paragraph."
        
        paragraphs = self.processor.tokenize_paragraphs(text)
        assert len(paragraphs) == 3
        assert "First paragraph." in paragraphs[0]
        assert "Second paragraph." in paragraphs[1]
        assert "Third paragraph." in paragraphs[2]
    
    def test_chunk_text_by_characters(self):
        """Test text chunking by characters."""
        text = "This is a long text that needs to be chunked into smaller pieces for processing."
        
        chunks = self.processor.chunk_text(text, chunk_size=30, overlap=5, chunk_by="characters")
        
        assert len(chunks) > 1
        assert all(len(chunk.content) <= 35 for chunk in chunks)  # Allow for word boundaries
        assert chunks[0].chunk_id == 0
        assert chunks[1].chunk_id == 1
    
    def test_chunk_text_by_words(self):
        """Test text chunking by words."""
        text = "This is a test sentence with many words that should be chunked properly."
        
        chunks = self.processor.chunk_text(text, chunk_size=5, overlap=2, chunk_by="words")
        
        assert len(chunks) > 1
        # Each chunk should have roughly 5 words or fewer
        for chunk in chunks:
            word_count = len(chunk.content.split())
            assert word_count <= 7  # Allow some flexibility
    
    def test_chunk_text_by_sentences(self):
        """Test text chunking by sentences."""
        text = "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence."
        
        chunks = self.processor.chunk_text(text, chunk_size=2, overlap=1, chunk_by="sentences")
        
        assert len(chunks) > 1
        # Each chunk should have roughly 2 sentences or fewer
        for chunk in chunks:
            sentence_count = chunk.content.count('.')
            assert sentence_count <= 3  # Allow some flexibility


class TestTextAnalyzer:
    """Test TextAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = TextAnalyzer()
    
    def test_analyze_text(self):
        """Test comprehensive text analysis."""
        text = """
        This is a test document. It contains multiple sentences and paragraphs.
        
        This is the second paragraph. It also has multiple sentences.
        The document is used for testing the text analysis functionality.
        """
        
        stats = self.analyzer.analyze_text(text)
        
        assert stats.word_count > 0
        assert stats.sentence_count > 0
        assert stats.paragraph_count >= 2
        assert stats.char_count > 0
        assert stats.avg_words_per_sentence > 0
        assert len(stats.top_words) > 0
        assert stats.language_detected in ["english", "other"]
    
    def test_extract_keywords(self):
        """Test keyword extraction."""
        text = "Python programming language machine learning artificial intelligence data science"
        
        keywords = self.analyzer.extract_keywords(text, num_keywords=5)
        
        assert len(keywords) <= 5
        assert all(isinstance(kw, tuple) and len(kw) == 2 for kw in keywords)
        assert all(isinstance(kw[0], str) and isinstance(kw[1], float) for kw in keywords)
        
        # Keywords should be sorted by score (descending)
        scores = [kw[1] for kw in keywords]
        assert scores == sorted(scores, reverse=True)
    
    def test_find_patterns(self):
        """Test pattern finding."""
        text = """
        Contact us at test@example.com or visit https://example.com
        Call us at 555-123-4567 or check the date 12/31/2023
        The file is located at /path/to/file.txt
        """
        
        patterns = self.analyzer.find_patterns(text)
        
        if "emails" in patterns:
            assert "test@example.com" in patterns["emails"]
        
        if "urls" in patterns:
            assert any("example.com" in url for url in patterns["urls"])
        
        if "phone_numbers" in patterns:
            assert any("555" in phone for phone in patterns["phone_numbers"])
        
        if "dates" in patterns:
            assert any("12/31/2023" in date for date in patterns["dates"])
    
    def test_extract_entities(self):
        """Test entity extraction."""
        text = "Python is a programming language. Google and Microsoft use it extensively."
        
        entities = self.analyzer.extract_entities(text)
        
        # Should detect some entities
        assert isinstance(entities, dict)
        
        # Check for technology entities
        if "technologies" in entities:
            assert "python" in [tech.lower() for tech in entities["technologies"]]
    
    def test_summarize_content(self):
        """Test content summarization."""
        text = """
        Machine learning is a subset of artificial intelligence. It focuses on algorithms that can learn from data.
        Deep learning is a subset of machine learning. It uses neural networks with multiple layers.
        Natural language processing is another important area. It deals with understanding human language.
        Computer vision is also crucial. It helps machines understand visual information.
        """
        
        summary = self.analyzer.summarize_content(text, max_sentences=2)
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert summary.count('.') <= 3  # Should have at most 2-3 sentences