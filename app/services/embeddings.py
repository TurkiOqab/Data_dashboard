"""
Embeddings Service

Handles text embedding generation and vector storage using ChromaDB.
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions


class EmbeddingsService:
    """Manages text embeddings and vector storage."""

    def __init__(
        self,
        persist_dir: Optional[str] = None,
        collection_name: str = "slides"
    ):
        self.persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB with persistence
        self.client = chromadb.PersistentClient(path=self.persist_dir)

        # Use default embedding function (all-MiniLM-L6-v2)
        # This is a good balance of speed and quality for semantic search
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
            metadata={"description": "Slide content embeddings"}
        )

    def add_slide(
        self,
        slide_id: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Add a single slide's content to the vector store.

        Args:
            slide_id: Unique identifier for the slide
            content: Text content to embed
            metadata: Additional metadata (slide_number, filename, etc.)
        """
        # Ensure metadata values are valid types for ChromaDB
        clean_metadata = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                clean_metadata[key] = value
            elif isinstance(value, list):
                clean_metadata[key] = str(value)
            elif value is None:
                clean_metadata[key] = ""
            else:
                clean_metadata[key] = str(value)

        self.collection.upsert(
            ids=[slide_id],
            documents=[content],
            metadatas=[clean_metadata]
        )

    def add_slides_batch(
        self,
        slides: List[Dict[str, Any]]
    ) -> None:
        """
        Add multiple slides to the vector store.

        Args:
            slides: List of dicts with 'id', 'content', and 'metadata' keys
        """
        if not slides:
            return

        ids = []
        documents = []
        metadatas = []

        for slide in slides:
            ids.append(slide['id'])
            documents.append(slide['content'])

            # Clean metadata
            clean_metadata = {}
            for key, value in slide.get('metadata', {}).items():
                if isinstance(value, (str, int, float, bool)):
                    clean_metadata[key] = value
                elif value is None:
                    clean_metadata[key] = ""
                else:
                    clean_metadata[key] = str(value)
            metadatas.append(clean_metadata)

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant slides using semantic similarity.

        Args:
            query: Search query text
            n_results: Number of results to return
            filter_metadata: Optional metadata filters

        Returns:
            List of matching slides with scores
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=filter_metadata
        )

        # Format results
        formatted = []
        if results and results['ids'] and results['ids'][0]:
            for i, slide_id in enumerate(results['ids'][0]):
                formatted.append({
                    'id': slide_id,
                    'content': results['documents'][0][i] if results['documents'] else "",
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else 0
                })

        return formatted

    def get_slide(self, slide_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific slide by ID."""
        results = self.collection.get(
            ids=[slide_id],
            include=['documents', 'metadatas']
        )

        if results and results['ids']:
            return {
                'id': results['ids'][0],
                'content': results['documents'][0] if results['documents'] else "",
                'metadata': results['metadatas'][0] if results['metadatas'] else {}
            }
        return None

    def delete_by_filename(self, filename: str) -> None:
        """Delete all slides from a specific file."""
        # Get all IDs for this file
        results = self.collection.get(
            where={"filename": filename},
            include=[]
        )

        if results and results['ids']:
            self.collection.delete(ids=results['ids'])

    def clear_collection(self) -> None:
        """Clear all data from the collection."""
        # Delete and recreate collection
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name="slides",
            embedding_function=self.embedding_fn,
            metadata={"description": "Slide content embeddings"}
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            "total_slides": self.collection.count(),
            "persist_dir": self.persist_dir
        }


def create_slide_embedding_content(slide_data: Dict[str, Any]) -> str:
    """
    Create optimized text content for embedding from slide data.

    This function formats slide content to maximize semantic search quality.
    """
    parts = []

    # Title is important for search
    if slide_data.get('title'):
        parts.append(f"Title: {slide_data['title']}")

    # Main text content
    if slide_data.get('text_content'):
        text = slide_data['text_content']
        if isinstance(text, list):
            text = " ".join(text)
        parts.append(text)

    # Table content (converted to readable format)
    if slide_data.get('tables'):
        for table in slide_data['tables']:
            if isinstance(table, dict) and table.get('rows'):
                # Flatten table to text
                for row in table['rows']:
                    parts.append(" | ".join(str(cell) for cell in row))

    # Notes can contain valuable context
    if slide_data.get('raw_notes'):
        parts.append(f"Notes: {slide_data['raw_notes']}")

    # Visual indicators
    if slide_data.get('has_chart'):
        parts.append("[Contains chart/visualization]")

    if slide_data.get('has_image'):
        parts.append("[Contains image]")

    return " ".join(parts)
