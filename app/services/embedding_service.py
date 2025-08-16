"""
Embedding service for RAG integration
- Generates sentence-transformer embeddings
- Persists vectors into Supabase table `kudwa_embeddings`
"""
from __future__ import annotations

import json
import uuid
from typing import Any, Dict, List, Optional

import numpy as np
import structlog
from sentence_transformers import SentenceTransformer

from app.services.supabase_client import supabase_service

logger = structlog.get_logger(__name__)


class EmbeddingService:
    """Create and persist embeddings for documents and entities."""

    def __init__(self) -> None:
        # Keep model small and aligned with RAGGraphManager
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_text(self, text: str) -> List[float]:
        try:
            vec = self.model.encode([text])[0]
            # Ensure JSON serializable
            return np.asarray(vec, dtype=np.float32).tolist()
        except Exception as e:
            logger.error("Embedding generation failed", error=str(e))
            raise

    def _insert_embedding(
        self,
        *,
        content: str,
        embedding: List[float],
        source_kind: str,
        source_id: str,
        ontology_class_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        try:
            payload = {
                "id": str(uuid.uuid4()),
                "content": content,
                "embedding": embedding,
                "source_kind": source_kind,  # e.g., 'document' | 'entity'
                "source_id": source_id,
                "ontology_class_id": ontology_class_id,
                "metadata": metadata or {},
            }
            supabase_service.client.table("kudwa_embeddings").insert(payload).execute()
        except Exception as e:
            logger.warning("Failed to persist embedding", error=str(e), source_kind=source_kind)

    def index_document_and_entities(
        self,
        *,
        document_id: str,
        filename: str,
        data: Dict[str, Any],
        entities: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Create embeddings for the raw document and each extracted entity."""
        try:
            # 1) Document-level embedding
            doc_text = json.dumps(data)[:10000]
            doc_vec = self.embed_text(doc_text)
            self._insert_embedding(
                content=f"Document {filename}: {doc_text[:500]}",
                embedding=doc_vec,
                source_kind="document",
                source_id=document_id,
                metadata={"filename": filename},
            )

            # 2) Entity-level embeddings
            count = 0
            for ent in entities or []:
                name = ent.get("name") or "Unnamed"
                etype = ent.get("entity_type") or ent.get("type")
                props = ent.get("properties", {})
                # Compact string for semantic search
                content_str = (
                    f"{etype or 'entity'}: {name}. "
                    f"Key props: {json.dumps(props)[:800]}"
                )
                vec = self.embed_text(content_str)
                self._insert_embedding(
                    content=content_str,
                    embedding=vec,
                    source_kind="entity",
                    source_id=ent.get("id", document_id),
                    ontology_class_id=etype,
                    metadata={"document_id": document_id},
                )
                count += 1

            return {"document_vectors": 1, "entity_vectors": count}
        except Exception as e:
            logger.error("Indexing document/entities for RAG failed", error=str(e))
            return {"document_vectors": 0, "entity_vectors": 0, "error": str(e)}


# Global instance
embedding_service = EmbeddingService()

