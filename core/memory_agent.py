"""
OMNI Memory Agent

Implements vector database memory using ChromaDB for Retrieval-Augmented Generation (RAG).
Prevents context window overflow by storing and retrieving relevant code chunks semantically.

This agent maintains project context across the codebase, enabling:
- Semantic code search (e.g., "where is the Stripe webhook handler?")
- Context-aware code generation
- Efficient retrieval of relevant code snippets
"""

import os
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from rich.console import Console


console = Console()


class MemoryAgent:
    def __init__(self):
        """
        Initialize the Memory Agent.

        The agent manages a ChromaDB collection for vector-based code retrieval.
        """
        self.client: Optional[chromadb.Client] = None
        self.collection: Optional[chromadb.Collection] = None
        self.collection_name: str = ""

    async def a_init(self, collection_name: str):
        """
        Initialize ChromaDB client and create/get collection.

        Args:
            collection_name: Name of the collection (typically the project name)
        """
        self.collection_name = collection_name

        # Run ChromaDB initialization in executor (ChromaDB is synchronous)
        loop = asyncio.get_event_loop()

        def _init_chromadb():
            # Create persistent ChromaDB client
            client = chromadb.PersistentClient(
                path="./.omni_memory",
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )

            # Get or create collection
            collection = client.get_or_create_collection(
                name=collection_name,
                metadata={"description": f"Vector memory for {collection_name} project"}
            )

            return client, collection

        self.client, self.collection = await loop.run_in_executor(None, _init_chromadb)
        console.print(f"[green]✓[/green] Memory initialized: {collection_name}")

    async def a_add_document(self, file_path: str, content: str, metadata: dict):
        """
        Add document to vector memory with automatic chunking.

        The content is split into overlapping chunks to ensure semantic continuity.
        Each chunk is stored with its file path and metadata for retrieval.

        Args:
            file_path: Path to the file (e.g., "src/app/api/webhooks/stripe/route.ts")
            content: Full file content
            metadata: Additional metadata (e.g., {"language": "typescript", "file_type": "api_route"})
        """
        if not self.collection:
            raise RuntimeError("Memory not initialized. Call a_init() first.")

        # Chunk the content with overlap for semantic continuity
        chunks = self._chunk_text(content, chunk_size=500, overlap=50)

        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{file_path}::chunk_{i}"
            chunk_metadata = {
                "file_path": file_path,
                "chunk_index": i,
                "total_chunks": len(chunks),
                **metadata
            }

            documents.append(chunk)
            metadatas.append(chunk_metadata)
            ids.append(chunk_id)

        # Add to ChromaDB (run in executor since it's synchronous)
        loop = asyncio.get_event_loop()

        def _add_to_chromadb():
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

        await loop.run_in_executor(None, _add_to_chromadb)

    async def a_retrieve_context(self, query: str, n_results: int = 5) -> str:
        """
        Retrieve relevant context from vector memory using semantic search.

        Args:
            query: Search query (e.g., "where is the Stripe webhook handler?")
            n_results: Number of relevant chunks to return (default: 5)

        Returns:
            Concatenated context string from the top relevant code chunks,
            formatted with file references for easy navigation.

        Example:
            >>> context = await memory.a_retrieve_context("Stripe webhook handler")
            >>> print(context)
            # From: src/app/api/webhooks/stripe/route.ts
            export async function POST(req: Request) {
              const signature = req.headers.get("stripe-signature");
              ...
            }
        """
        if not self.collection:
            raise RuntimeError("Memory not initialized. Call a_init() first.")

        # Query ChromaDB (run in executor since it's synchronous)
        loop = asyncio.get_event_loop()

        def _query_chromadb():
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            return results

        results = await loop.run_in_executor(None, _query_chromadb)

        # Extract and concatenate documents
        if results and results.get("documents") and len(results["documents"]) > 0:
            documents = results["documents"][0]  # First query's results
            metadatas = results["metadatas"][0] if results.get("metadatas") else []

            # Build context string with file references
            context_parts = []
            for doc, meta in zip(documents, metadatas):
                file_path = meta.get("file_path", "unknown")
                chunk_index = meta.get("chunk_index", 0)
                context_parts.append(f"# From: {file_path} (chunk {chunk_index})\n{doc}\n")

            return "\n---\n".join(context_parts)

        return ""

    async def a_clear_collection(self):
        """
        Clear all documents from the current collection.

        Useful for resetting project memory or starting fresh.
        """
        if not self.collection:
            raise RuntimeError("Memory not initialized. Call a_init() first.")

        loop = asyncio.get_event_loop()

        def _clear_chromadb():
            # Delete and recreate collection
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": f"Vector memory for {self.collection_name} project"}
            )

        await loop.run_in_executor(None, _clear_chromadb)
        console.print(f"[yellow]⊙[/yellow] Memory cleared: {self.collection_name}")

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks for semantic continuity.

        Attempts to break at natural boundaries (newlines, spaces) to preserve
        code structure and readability.

        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk (default: 500)
            overlap: Characters to overlap between chunks (default: 50)

        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at natural boundaries
            if end < len(text):
                # Look for newline in the last 100 chars
                newline_pos = text.rfind("\n", start, end)
                if newline_pos > start:
                    end = newline_pos + 1
                else:
                    # Look for space
                    space_pos = text.rfind(" ", start, end)
                    if space_pos > start:
                        end = space_pos + 1

            chunk = text[start:end].strip()
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)

            # Move to next chunk with overlap
            start = end - overlap

        return chunks

    async def a_get_stats(self) -> Dict[str, int]:
        """
        Get statistics about the current collection.

        Returns:
            Dictionary with collection statistics (e.g., {"document_count": 150})
        """
        if not self.collection:
            raise RuntimeError("Memory not initialized. Call a_init() first.")

        loop = asyncio.get_event_loop()

        def _get_stats():
            count = self.collection.count()
            return {"document_count": count}

        return await loop.run_in_executor(None, _get_stats)
