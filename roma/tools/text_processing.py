"""
Text processing utilities for content analysis and natural language processing.
"""

import re
import string
from typing import List, Dict, Set, Optional, Tuple, Union
from collections import Counter, defaultdict
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class TextStats:
    """Statistics about a text document."""
    char_count: int
    word_count: int
    sentence_count: int
    paragraph_count: int
    line_count: int
    avg_words_per_sentence: float
    avg_sentences_per_paragraph: float
    readability_score: float
    language_detected: str
    top_words: List[Tuple[str, int]]


@dataclass
class TextChunk:
    """Represents a chunk of text with metadata."""
    content: str
    start_position: int
    end_position: int
    chunk_id: int
    metadata: Dict


class TextProcessor:
    """Handles text preprocessing, cleaning, and basic analysis."""
    
    def __init__(self):
        self.stop_words = self._load_stop_words()
        self.punctuation_translator = str.maketrans('', '', string.punctuation)
    
    def _load_stop_words(self) -> Set[str]:
        """Load common English stop words."""
        # Basic stop words - in production, you might want to use NLTK or spaCy
        stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'would', 'you', 'your', 'have', 'had',
            'but', 'not', 'or', 'this', 'they', 'we', 'she', 'his', 'her',
            'him', 'them', 'their', 'what', 'which', 'who', 'when', 'where',
            'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most',
            'other', 'some', 'such', 'no', 'nor', 'only', 'own', 'same', 'so',
            'than', 'too', 'very', 'can', 'will', 'just', 'should', 'now'
        }
        return stop_words
    
    def clean_text(self, text: str, 
                   remove_punctuation: bool = False,
                   remove_numbers: bool = False,
                   remove_extra_whitespace: bool = True,
                   to_lowercase: bool = False) -> str:
        """
        Clean and preprocess text.
        
        Args:
            text: Input text
            remove_punctuation: Remove punctuation
            remove_numbers: Remove numeric characters
            remove_extra_whitespace: Remove extra whitespace
            to_lowercase: Convert to lowercase
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        cleaned = text
        
        if to_lowercase:
            cleaned = cleaned.lower()
        
        if remove_punctuation:
            cleaned = cleaned.translate(self.punctuation_translator)
        
        if remove_numbers:
            cleaned = re.sub(r'\d+', '', cleaned)
        
        if remove_extra_whitespace:
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def tokenize_words(self, text: str, 
                      remove_stop_words: bool = False,
                      min_word_length: int = 1) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Input text
            remove_stop_words: Remove stop words
            min_word_length: Minimum word length
            
        Returns:
            List of tokens
        """
        if not text:
            return []
        
        # Basic word tokenization
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter words
        filtered_words = []
        for word in words:
            if len(word) >= min_word_length:
                if not remove_stop_words or word not in self.stop_words:
                    filtered_words.append(word)
        
        return filtered_words
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """
        Tokenize text into sentences.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        if not text:
            return []
        
        # Basic sentence tokenization
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def tokenize_paragraphs(self, text: str) -> List[str]:
        """
        Tokenize text into paragraphs.
        
        Args:
            text: Input text
            
        Returns:
            List of paragraphs
        """
        if not text:
            return []
        
        paragraphs = re.split(r'\n\s*\n', text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        return paragraphs
    
    def chunk_text(self, text: str, 
                   chunk_size: int = 1000,
                   overlap: int = 100,
                   chunk_by: str = "characters") -> List[TextChunk]:
        """
        Chunk text into smaller pieces with optional overlap.
        
        Args:
            text: Input text
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
            chunk_by: Method to chunk by ("characters", "words", "sentences")
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        chunks = []
        
        if chunk_by == "characters":
            chunks = self._chunk_by_characters(text, chunk_size, overlap)
        elif chunk_by == "words":
            chunks = self._chunk_by_words(text, chunk_size, overlap)
        elif chunk_by == "sentences":
            chunks = self._chunk_by_sentences(text, chunk_size, overlap)
        else:
            raise ValueError(f"Invalid chunk_by method: {chunk_by}")
        
        return chunks
    
    def _chunk_by_characters(self, text: str, chunk_size: int, overlap: int) -> List[TextChunk]:
        """Chunk text by character count."""
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            
            # Try to break at word boundary if possible
            if end < len(text):
                last_space = text.rfind(' ', start, end)
                if last_space > start:
                    end = last_space
            
            chunk_content = text[start:end].strip()
            if chunk_content:
                chunks.append(TextChunk(
                    content=chunk_content,
                    start_position=start,
                    end_position=end,
                    chunk_id=chunk_id,
                    metadata={"method": "characters", "size": len(chunk_content)}
                ))
                chunk_id += 1
            
            start = max(start + 1, end - overlap)
        
        return chunks
    
    def _chunk_by_words(self, text: str, chunk_size: int, overlap: int) -> List[TextChunk]:
        """Chunk text by word count."""
        words = self.tokenize_words(text, remove_stop_words=False)
        chunks = []
        chunk_id = 0
        
        start_idx = 0
        while start_idx < len(words):
            end_idx = min(start_idx + chunk_size, len(words))
            chunk_words = words[start_idx:end_idx]
            
            if chunk_words:
                chunk_content = ' '.join(chunk_words)
                chunks.append(TextChunk(
                    content=chunk_content,
                    start_position=start_idx,
                    end_position=end_idx,
                    chunk_id=chunk_id,
                    metadata={"method": "words", "word_count": len(chunk_words)}
                ))
                chunk_id += 1
            
            start_idx = max(start_idx + 1, end_idx - overlap)
        
        return chunks
    
    def _chunk_by_sentences(self, text: str, chunk_size: int, overlap: int) -> List[TextChunk]:
        """Chunk text by sentence count."""
        sentences = self.tokenize_sentences(text)
        chunks = []
        chunk_id = 0
        
        start_idx = 0
        while start_idx < len(sentences):
            end_idx = min(start_idx + chunk_size, len(sentences))
            chunk_sentences = sentences[start_idx:end_idx]
            
            if chunk_sentences:
                chunk_content = '. '.join(chunk_sentences) + '.'
                chunks.append(TextChunk(
                    content=chunk_content,
                    start_position=start_idx,
                    end_position=end_idx,
                    chunk_id=chunk_id,
                    metadata={"method": "sentences", "sentence_count": len(chunk_sentences)}
                ))
                chunk_id += 1
            
            start_idx = max(start_idx + 1, end_idx - overlap)
        
        return chunks


class TextAnalyzer:
    """Advanced text analysis including statistics and pattern detection."""
    
    def __init__(self):
        self.processor = TextProcessor()
    
    def analyze_text(self, text: str) -> TextStats:
        """
        Perform comprehensive text analysis.
        
        Args:
            text: Input text
            
        Returns:
            TextStats object with analysis results
        """
        if not text:
            return TextStats(0, 0, 0, 0, 0, 0.0, 0.0, 0.0, "unknown", [])
        
        # Basic counts
        char_count = len(text)
        word_count = len(self.processor.tokenize_words(text))
        sentences = self.processor.tokenize_sentences(text)
        sentence_count = len(sentences)
        paragraphs = self.processor.tokenize_paragraphs(text)
        paragraph_count = len(paragraphs)
        line_count = text.count('\n') + 1
        
        # Averages
        avg_words_per_sentence = word_count / sentence_count if sentence_count > 0 else 0
        avg_sentences_per_paragraph = sentence_count / paragraph_count if paragraph_count > 0 else 0
        
        # Readability (simplified Flesch Reading Ease)
        readability_score = self._calculate_readability(text, word_count, sentence_count)
        
        # Language detection (simplified)
        language_detected = self._detect_language(text)
        
        # Top words
        words = self.processor.tokenize_words(text, remove_stop_words=True)
        word_freq = Counter(words)
        top_words = word_freq.most_common(10)
        
        return TextStats(
            char_count=char_count,
            word_count=word_count,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            line_count=line_count,
            avg_words_per_sentence=avg_words_per_sentence,
            avg_sentences_per_paragraph=avg_sentences_per_paragraph,
            readability_score=readability_score,
            language_detected=language_detected,
            top_words=top_words
        )
    
    def _calculate_readability(self, text: str, word_count: int, sentence_count: int) -> float:
        """Calculate simplified readability score."""
        if sentence_count == 0 or word_count == 0:
            return 0.0
        
        # Count syllables (simplified)
        syllable_count = self._count_syllables(text)
        
        # Flesch Reading Ease formula (simplified)
        if sentence_count > 0 and word_count > 0:
            avg_sentence_length = word_count / sentence_count
            avg_syllables_per_word = syllable_count / word_count
            
            score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
            return max(0, min(100, score))
        
        return 0.0
    
    def _count_syllables(self, text: str) -> int:
        """Simplified syllable counting."""
        words = self.processor.tokenize_words(text)
        syllable_count = 0
        
        for word in words:
            # Simple syllable counting heuristic
            vowels = 'aeiouy'
            syllables = 0
            prev_was_vowel = False
            
            for char in word.lower():
                is_vowel = char in vowels
                if is_vowel and not prev_was_vowel:
                    syllables += 1
                prev_was_vowel = is_vowel
            
            # Adjust for common patterns
            if word.endswith('e'):
                syllables -= 1
            if syllables == 0:
                syllables = 1
            
            syllable_count += syllables
        
        return syllable_count
    
    def _detect_language(self, text: str) -> str:
        """Simplified language detection."""
        # This is a very basic implementation
        # In production, you'd want to use a proper language detection library
        
        words = self.processor.tokenize_words(text, remove_stop_words=False)
        if not words:
            return "unknown"
        
        # Check for common English words
        english_indicators = {'the', 'and', 'to', 'of', 'a', 'in', 'is', 'it', 'you', 'that'}
        english_count = sum(1 for word in words[:100] if word.lower() in english_indicators)
        
        if english_count > 5:
            return "english"
        else:
            return "other"
    
    def extract_keywords(self, text: str, 
                        num_keywords: int = 10,
                        min_word_length: int = 3) -> List[Tuple[str, float]]:
        """
        Extract keywords using TF-IDF-like scoring.
        
        Args:
            text: Input text
            num_keywords: Number of keywords to extract
            min_word_length: Minimum word length
            
        Returns:
            List of (keyword, score) tuples
        """
        words = self.processor.tokenize_words(text, remove_stop_words=True, min_word_length=min_word_length)
        
        if not words:
            return []
        
        # Calculate word frequencies
        word_freq = Counter(words)
        total_words = len(words)
        
        # Calculate scores (simplified TF-IDF)
        keyword_scores = {}
        for word, freq in word_freq.items():
            tf = freq / total_words
            # Simplified IDF (would need document corpus for real IDF)
            idf = 1.0 / (1.0 + freq)  # Inverse frequency as proxy
            score = tf * idf
            keyword_scores[word] = score
        
        # Sort by score and return top keywords
        sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_keywords[:num_keywords]
    
    def find_patterns(self, text: str) -> Dict[str, List[str]]:
        """
        Find common patterns in text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of pattern types and their matches
        """
        patterns = {
            "emails": re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text),
            "urls": re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text),
            "phone_numbers": re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text),
            "dates": re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text),
            "numbers": re.findall(r'\b\d+\.?\d*\b', text),
            "code_blocks": re.findall(r'```[\s\S]*?```|`[^`\n]+`', text),
            "file_paths": re.findall(r'[a-zA-Z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*|/(?:[^/\0\r\n]+/)*[^/\0\r\n]*', text)
        }
        
        return {k: v for k, v in patterns.items() if v}
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities (simplified approach).
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of entity types and their values
        """
        entities = {
            "organizations": [],
            "locations": [],
            "persons": [],
            "technologies": []
        }
        
        # Simple pattern-based entity extraction
        # This is very basic - in production, use NER libraries like spaCy
        
        # Look for capitalized words that might be entities
        capitalized_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        # Technology keywords
        tech_keywords = {
            'python', 'javascript', 'java', 'react', 'nodejs', 'docker', 'kubernetes',
            'aws', 'azure', 'google cloud', 'tensorflow', 'pytorch', 'mongodb', 'sql',
            'api', 'rest', 'graphql', 'microservices', 'devops', 'ci/cd'
        }
        
        words_lower = text.lower()
        for tech in tech_keywords:
            if tech in words_lower:
                entities["technologies"].append(tech)
        
        # This is a simplified approach - real NER would be much more sophisticated
        entities["organizations"] = [word for word in capitalized_words if len(word) > 2][:10]
        
        return {k: list(set(v)) for k, v in entities.items() if v}
    
    def summarize_content(self, text: str, max_sentences: int = 3) -> str:
        """
        Create a simple extractive summary.
        
        Args:
            text: Input text
            max_sentences: Maximum sentences in summary
            
        Returns:
            Summary text
        """
        sentences = self.processor.tokenize_sentences(text)
        
        if len(sentences) <= max_sentences:
            return '. '.join(sentences) + '.'
        
        # Score sentences based on word frequency
        words = self.processor.tokenize_words(text, remove_stop_words=True)
        word_freq = Counter(words)
        
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            sentence_words = self.processor.tokenize_words(sentence, remove_stop_words=True)
            score = sum(word_freq.get(word, 0) for word in sentence_words)
            sentence_scores[i] = score / len(sentence_words) if sentence_words else 0
        
        # Select top sentences
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
        selected_indices = sorted([idx for idx, _ in top_sentences[:max_sentences]])
        
        summary = '. '.join([sentences[i] for i in selected_indices]) + '.'
        return summary