"""
Advanced retrieval tools using dense embeddings, BM25, and hybrid approaches.
"""

import os
import pickle
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import numpy as np
from collections import defaultdict, Counter
import math
import re

from ..models.state import SearchResult


class DenseRetrievalTool:
    """Dense retrieval using embeddings (simulated with TF-IDF for now)."""
    
    def __init__(self, workspace_path: str, cache_dir: Optional[str] = None):
        self.workspace_path = Path(workspace_path)
        self.cache_dir = Path(cache_dir) if cache_dir else self.workspace_path / ".research_cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        self.documents = {}  # file_path -> content
        self.embeddings = {}  # file_path -> embedding
        self.vocabulary = set()
        self.idf_scores = {}
        
    def index_documents(self, file_paths: List[str], chunk_size: int = 1000) -> None:
        """Index documents for dense retrieval."""
        print(f"Indexing {len(file_paths)} documents...")
        
        # Load or create document cache
        cache_file = self.cache_dir / "document_cache.pkl"
        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
                self.documents = cached_data.get('documents', {})
                self.vocabulary = cached_data.get('vocabulary', set())
        
        # Process documents
        for file_path in file_paths:
            if file_path not in self.documents:
                content = self._read_file(file_path)
                if content:
                    # Split into chunks if document is large
                    if len(content) > chunk_size:
                        chunks = self._split_into_chunks(content, chunk_size)
                        for i, chunk in enumerate(chunks):
                            chunk_path = f"{file_path}#chunk_{i}"
                            self.documents[chunk_path] = chunk
                            self.vocabulary.update(self._tokenize(chunk))
                    else:
                        self.documents[file_path] = content
                        self.vocabulary.update(self._tokenize(content))
        
        # Calculate IDF scores
        self._calculate_idf_scores()
        
        # Generate embeddings (TF-IDF vectors)
        self._generate_embeddings()
        
        # Save cache
        with open(cache_file, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'vocabulary': self.vocabulary,
                'embeddings': self.embeddings,
                'idf_scores': self.idf_scores
            }, f)
        
        print(f"Indexed {len(self.documents)} document chunks")
    
    def search(self, query: str, top_k: int = 10, threshold: float = 0.1) -> List[SearchResult]:
        """Search using dense retrieval."""
        if not self.embeddings:
            return []
        
        # Generate query embedding
        query_embedding = self._text_to_vector(query)
        
        # Calculate similarities
        similarities = []
        for doc_path, doc_embedding in self.embeddings.items():
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            if similarity >= threshold:
                similarities.append((doc_path, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Convert to SearchResults
        results = []
        for doc_path, similarity in similarities[:top_k]:
            # Extract original file path if it's a chunk
            original_path = doc_path.split('#')[0]
            content = self.documents[doc_path]
            
            results.append(SearchResult(
                source=original_path,
                content=content[:500] + "..." if len(content) > 500 else content,
                relevance_score=similarity,
                metadata={
                    "similarity": similarity,
                    "document_chunk": doc_path,
                    "content_length": len(content)
                },
                search_query=query,
                tool_used="dense_retrieval"
            ))
        
        return results
    
    def _read_file(self, file_path: str) -> Optional[str]:
        """Read file content."""
        full_path = self.workspace_path / file_path
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except:
            return None
    
    def _split_into_chunks(self, text: str, chunk_size: int) -> List[str]:
        """Split text into chunks."""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), chunk_size // 10):  # Overlap chunks
            chunk_words = words[i:i + chunk_size // 10]
            chunks.append(' '.join(chunk_words))
        
        return chunks
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        # Remove non-alphanumeric characters and convert to lowercase
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
        return [word for word in text.split() if len(word) > 2]
    
    def _calculate_idf_scores(self) -> None:
        """Calculate IDF scores for vocabulary."""
        doc_count = len(self.documents)
        word_doc_count = defaultdict(int)
        
        for content in self.documents.values():
            words_in_doc = set(self._tokenize(content))
            for word in words_in_doc:
                word_doc_count[word] += 1
        
        for word in self.vocabulary:
            self.idf_scores[word] = math.log(doc_count / (word_doc_count[word] + 1))
    
    def _text_to_vector(self, text: str) -> np.ndarray:
        """Convert text to TF-IDF vector."""
        words = self._tokenize(text)
        word_count = Counter(words)
        
        vector = np.zeros(len(self.vocabulary))
        vocab_list = sorted(list(self.vocabulary))
        
        for i, word in enumerate(vocab_list):
            if word in word_count:
                tf = word_count[word] / len(words)
                idf = self.idf_scores.get(word, 0)
                vector[i] = tf * idf
        
        # Normalize vector
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector
    
    def _generate_embeddings(self) -> None:
        """Generate embeddings for all documents."""
        for doc_path, content in self.documents.items():
            self.embeddings[doc_path] = self._text_to_vector(content)
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)


class BM25RetrievalTool:
    """BM25 retrieval implementation."""
    
    def __init__(self, workspace_path: str, k1: float = 1.5, b: float = 0.75):
        self.workspace_path = Path(workspace_path)
        self.k1 = k1
        self.b = b
        
        self.documents = {}  # doc_id -> content
        self.doc_lengths = {}  # doc_id -> length
        self.avg_doc_length = 0
        self.term_frequencies = {}  # term -> {doc_id: frequency}
        self.document_frequencies = {}  # term -> number of docs containing term
        self.vocabulary = set()
    
    def index_documents(self, file_paths: List[str]) -> None:
        """Index documents for BM25 retrieval."""
        print(f"Building BM25 index for {len(file_paths)} documents...")
        
        # Read and tokenize documents
        total_length = 0
        for file_path in file_paths:
            content = self._read_file(file_path)
            if content:
                tokens = self._tokenize(content)
                self.documents[file_path] = tokens
                self.doc_lengths[file_path] = len(tokens)
                total_length += len(tokens)
                self.vocabulary.update(tokens)
        
        self.avg_doc_length = total_length / len(self.documents) if self.documents else 0
        
        # Build term frequencies and document frequencies
        for doc_id, tokens in self.documents.items():
            token_counts = Counter(tokens)
            
            for term, freq in token_counts.items():
                if term not in self.term_frequencies:
                    self.term_frequencies[term] = {}
                self.term_frequencies[term][doc_id] = freq
                
                if term not in self.document_frequencies:
                    self.document_frequencies[term] = 0
                self.document_frequencies[term] += 1
        
        print(f"BM25 index built: {len(self.vocabulary)} unique terms")
    
    def search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """Search using BM25 scoring."""
        if not self.documents:
            return []
        
        query_terms = self._tokenize(query)
        doc_scores = {}
        
        # Calculate BM25 scores for each document
        for doc_id in self.documents:
            score = 0.0
            
            for term in query_terms:
                if term in self.term_frequencies and doc_id in self.term_frequencies[term]:
                    # Term frequency in document
                    tf = self.term_frequencies[term][doc_id]
                    
                    # Document frequency
                    df = self.document_frequencies[term]
                    
                    # IDF component
                    idf = math.log((len(self.documents) - df + 0.5) / (df + 0.5))
                    
                    # BM25 formula
                    numerator = tf * (self.k1 + 1)
                    denominator = tf + self.k1 * (1 - self.b + self.b * (self.doc_lengths[doc_id] / self.avg_doc_length))
                    
                    score += idf * (numerator / denominator)
            
            if score > 0:
                doc_scores[doc_id] = score
        
        # Sort by score
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Convert to SearchResults
        results = []
        for doc_id, score in sorted_docs[:top_k]:
            content = self._read_file(doc_id)
            if content:
                results.append(SearchResult(
                    source=doc_id,
                    content=content[:500] + "..." if len(content) > 500 else content,
                    relevance_score=min(score / 10.0, 1.0),  # Normalize score
                    metadata={
                        "bm25_score": score,
                        "query_terms_found": len([t for t in query_terms if t in self.term_frequencies and doc_id in self.term_frequencies[t]])
                    },
                    search_query=query,
                    tool_used="bm25_retrieval"
                ))
        
        return results
    
    def _read_file(self, file_path: str) -> Optional[str]:
        """Read file content."""
        full_path = self.workspace_path / file_path
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except:
            return None
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text for BM25."""
        # Remove non-alphanumeric characters and convert to lowercase
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
        return [word for word in text.split() if len(word) > 2]


class HybridRetrievalTool:
    """Hybrid retrieval combining dense and sparse methods."""
    
    def __init__(self, workspace_path: str, dense_weight: float = 0.6, sparse_weight: float = 0.4):
        self.workspace_path = workspace_path
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight
        
        self.dense_tool = DenseRetrievalTool(workspace_path)
        self.bm25_tool = BM25RetrievalTool(workspace_path)
    
    def index_documents(self, file_paths: List[str]) -> None:
        """Index documents for both dense and sparse retrieval."""
        print("Building hybrid index...")
        self.dense_tool.index_documents(file_paths)
        self.bm25_tool.index_documents(file_paths)
        print("Hybrid index complete")
    
    def search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """Search using hybrid approach."""
        # Get results from both methods
        dense_results = self.dense_tool.search(query, top_k * 2)
        sparse_results = self.bm25_tool.search(query, top_k * 2)
        
        # Combine and re-rank results
        combined_scores = {}
        
        # Add dense scores
        for result in dense_results:
            key = result.source
            if key not in combined_scores:
                combined_scores[key] = {"result": result, "dense_score": 0, "sparse_score": 0}
            combined_scores[key]["dense_score"] = result.relevance_score
        
        # Add sparse scores
        for result in sparse_results:
            key = result.source
            if key not in combined_scores:
                combined_scores[key] = {"result": result, "dense_score": 0, "sparse_score": 0}
            combined_scores[key]["sparse_score"] = result.relevance_score
        
        # Calculate hybrid scores
        hybrid_results = []
        for key, data in combined_scores.items():
            hybrid_score = (self.dense_weight * data["dense_score"] + 
                          self.sparse_weight * data["sparse_score"])
            
            result = data["result"]
            result.relevance_score = hybrid_score
            result.metadata["hybrid_score"] = hybrid_score
            result.metadata["dense_score"] = data["dense_score"]
            result.metadata["sparse_score"] = data["sparse_score"]
            result.tool_used = "hybrid_retrieval"
            
            hybrid_results.append(result)
        
        # Sort by hybrid score and return top k
        hybrid_results.sort(key=lambda x: x.relevance_score, reverse=True)
        return hybrid_results[:top_k]