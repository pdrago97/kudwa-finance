"""
RAG-Anything integration for knowledge graph generation and management
"""

import os
import json
import networkx as nx
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import structlog
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pyvis.network import Network

from app.services.supabase_client import SupabaseService
from app.core.config import settings

logger = structlog.get_logger(__name__)


class RAGGraphManager:
    """Manager for RAG operations and knowledge graph generation"""

    def __init__(self):
        self.supabase = SupabaseService()
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.graph = nx.DiGraph()
        self.embeddings_data = []  # Store embeddings and metadata
        self.entity_embeddings = {}
        
    async def initialize_vector_index(self):
        """Initialize vector index from Supabase embeddings using sklearn"""
        try:
            # Fetch all embeddings from Supabase (include metadata for our real vectors)
            embeddings_result = self.supabase.client.table("kudwa_embeddings")\
                .select("id, content, embedding, source_kind, source_id, ontology_class_id, metadata")\
                .execute()

            if not embeddings_result.data:
                logger.warning("No embeddings found in database")
                return

            # Prepare embeddings data
            self.embeddings_data = []

            for item in embeddings_result.data:
                # Try to get embedding from metadata (our real 384-dim vectors)
                embedding_vector = None
                if item.get("metadata") and item["metadata"].get("embedding_vector"):
                    embedding_vector = item["metadata"]["embedding_vector"]
                    # Ensure it's a list, not a string
                    if isinstance(embedding_vector, str):
                        try:
                            import json
                            embedding_vector = json.loads(embedding_vector)
                        except:
                            continue  # Skip if can't parse
                elif item.get("embedding") and not isinstance(item["embedding"], str):
                    # Fallback to the vector column if it's not a string representation
                    embedding_vector = item["embedding"]

                if embedding_vector and isinstance(embedding_vector, list):
                    self.embeddings_data.append({
                        "id": item["id"],
                        "content": item["content"],
                        "source_kind": item["source_kind"],
                        "source_id": item["source_id"],
                        "ontology_class_id": item.get("ontology_class_id"),
                        "embedding": np.array(embedding_vector, dtype=np.float32)
                    })

            if self.embeddings_data:
                logger.info(f"Vector index initialized with {len(self.embeddings_data)} embeddings")

        except Exception as e:
            logger.error("Failed to initialize vector index", error=str(e))
            raise
    
    async def build_knowledge_graph(self) -> Dict[str, Any]:
        """Build knowledge graph from ontology and data relationships"""
        try:
            # Clear existing graph
            self.graph.clear()
            
            # Add ontology classes as nodes
            await self._add_ontology_nodes()
            
            # Add ontology relationships as edges
            await self._add_ontology_relationships()
            
            # Add data instances as nodes
            await self._add_data_instances()
            
            # Add semantic relationships based on embeddings
            await self._add_semantic_relationships()
            
            # Generate graph statistics
            stats = self._calculate_graph_stats()
            
            return {
                "success": True,
                "nodes": self.graph.number_of_nodes(),
                "edges": self.graph.number_of_edges(),
                "stats": stats,
                "graph_data": self._export_graph_data()
            }
            
        except Exception as e:
            logger.error("Failed to build knowledge graph", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def _add_ontology_nodes(self):
        """Add ontology classes as graph nodes"""
        classes_result = self.supabase.client.table("kudwa_ontology_classes")\
            .select("class_id, label, domain, class_type, properties, confidence_score")\
            .eq("status", "active")\
            .execute()
        
        for cls in classes_result.data:
            self.graph.add_node(
                cls["class_id"],
                label=cls["label"],
                node_type="ontology_class",
                domain=cls["domain"],
                class_type=cls.get("class_type", ""),
                properties=cls.get("properties", {}),
                confidence=cls.get("confidence_score", 1.0),
                color="#FF6B6B",  # Red for ontology classes
                size=20
            )
    
    async def _add_ontology_relationships(self):
        """Add ontology relationships as graph edges"""
        relations_result = self.supabase.client.table("kudwa_ontology_relations")\
            .select("subject_class_id, predicate, object_class_id, properties, confidence_score")\
            .eq("status", "active")\
            .execute()
        
        for rel in relations_result.data:
            if self.graph.has_node(rel["subject_class_id"]) and self.graph.has_node(rel["object_class_id"]):
                self.graph.add_edge(
                    rel["subject_class_id"],
                    rel["object_class_id"],
                    predicate=rel["predicate"],
                    edge_type="ontology_relation",
                    properties=rel.get("properties", {}),
                    confidence=rel.get("confidence_score", 1.0),
                    color="#4ECDC4",  # Teal for ontology relations
                    width=2
                )
    
    async def _add_data_instances(self):
        """Add actual data instances as graph nodes"""
        # Add financial datasets
        datasets_result = self.supabase.client.table("kudwa_financial_datasets")\
            .select("id, name, description, period_start, period_end, currency")\
            .execute()
        
        for dataset in datasets_result.data:
            node_id = f"dataset_{dataset['id']}"
            self.graph.add_node(
                node_id,
                label=dataset["name"],
                node_type="data_instance",
                instance_type="financial_dataset",
                description=dataset.get("description", ""),
                period_start=dataset.get("period_start"),
                period_end=dataset.get("period_end"),
                currency=dataset.get("currency"),
                color="#45B7D1",  # Blue for data instances
                size=15
            )
        
        # Add financial observations
        observations_result = self.supabase.client.table("kudwa_financial_observations")\
            .select("id, dataset_id, account_name, amount, observation_type, period_start")\
            .limit(100)\
            .execute()
        
        for obs in observations_result.data:
            node_id = f"observation_{obs['id']}"
            self.graph.add_node(
                node_id,
                label=f"{obs.get('account_name', 'Unknown')} - {obs.get('amount', 0)}",
                node_type="data_instance",
                instance_type="financial_observation",
                account_name=obs.get("account_name"),
                amount=obs.get("amount"),
                observation_type=obs.get("observation_type"),
                period_start=obs.get("period_start"),
                color="#96CEB4",  # Green for observations
                size=10
            )
            
            # Connect to dataset
            dataset_node_id = f"dataset_{obs['dataset_id']}"
            if self.graph.has_node(dataset_node_id):
                self.graph.add_edge(
                    dataset_node_id,
                    node_id,
                    edge_type="contains",
                    color="#DDA0DD",  # Purple for data relations
                    width=1
                )
    
    async def _add_semantic_relationships(self):
        """Add semantic relationships based on embedding similarity"""
        if not self.embeddings_data:
            return

        # Find similar entities based on embeddings
        threshold = 0.7  # Similarity threshold

        for i, item_i in enumerate(self.embeddings_data):
            # Calculate similarities with all other embeddings
            similarities = []
            for j, item_j in enumerate(self.embeddings_data):
                if i != j:
                    # Calculate cosine similarity
                    sim = cosine_similarity(
                        item_i["embedding"].reshape(1, -1),
                        item_j["embedding"].reshape(1, -1)
                    )[0][0]
                    similarities.append((j, sim))

            # Sort by similarity and take top 10
            similarities.sort(key=lambda x: x[1], reverse=True)
            top_similarities = similarities[:10]

            for j, score in top_similarities:
                if score > threshold:
                    item_j = self.embeddings_data[j]

                    # Create semantic relationship
                    node_i = f"semantic_{item_i['id']}"
                    node_j = f"semantic_{item_j['id']}"

                    # Add nodes if they don't exist
                    if not self.graph.has_node(node_i):
                        self.graph.add_node(
                            node_i,
                            label=item_i["content"][:50] + "...",
                            node_type="semantic_entity",
                            content=item_i["content"],
                            source_kind=item_i["source_kind"],
                            color="#FFD93D",  # Yellow for semantic entities
                            size=8
                        )

                    if not self.graph.has_node(node_j):
                        self.graph.add_node(
                            node_j,
                            label=item_j["content"][:50] + "...",
                            node_type="semantic_entity",
                            content=item_j["content"],
                            source_kind=item_j["source_kind"],
                            color="#FFD93D",
                            size=8
                        )

                    # Add semantic similarity edge
                    self.graph.add_edge(
                        node_i,
                        node_j,
                        edge_type="semantic_similarity",
                        similarity_score=float(score),
                        color="#FF9999",  # Light red for semantic relations
                        width=max(1, int(score * 3))
                    )
    
    def _calculate_graph_stats(self) -> Dict[str, Any]:
        """Calculate graph statistics"""
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "node_types": {
                node_type: len([n for n, d in self.graph.nodes(data=True) if d.get("node_type") == node_type])
                for node_type in ["ontology_class", "data_instance", "semantic_entity"]
            },
            "edge_types": {
                edge_type: len([e for u, v, d in self.graph.edges(data=True) if d.get("edge_type") == edge_type])
                for edge_type in ["ontology_relation", "contains", "semantic_similarity"]
            },
            "density": nx.density(self.graph),
            "is_connected": nx.is_weakly_connected(self.graph) if self.graph.number_of_nodes() > 0 else False
        }
    
    def _export_graph_data(self) -> Dict[str, Any]:
        """Export graph data for visualization"""
        nodes = []
        edges = []
        
        for node_id, data in self.graph.nodes(data=True):
            nodes.append({
                "id": node_id,
                "label": data.get("label", node_id),
                "type": data.get("node_type", "unknown"),
                "color": data.get("color", "#CCCCCC"),
                "size": data.get("size", 10),
                **{k: v for k, v in data.items() if k not in ["label", "node_type", "color", "size"]}
            })
        
        for source, target, data in self.graph.edges(data=True):
            edges.append({
                "source": source,
                "target": target,
                "type": data.get("edge_type", "unknown"),
                "color": data.get("color", "#CCCCCC"),
                "width": data.get("width", 1),
                **{k: v for k, v in data.items() if k not in ["edge_type", "color", "width"]}
            })
        
        return {"nodes": nodes, "edges": edges}
    
    async def semantic_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Perform semantic search using cosine similarity"""
        try:
            if not self.embeddings_data:
                await self.initialize_vector_index()

            if not self.embeddings_data:
                return []

            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])
            query_vector = np.array(query_embedding, dtype=np.float32)

            # Calculate similarities with all embeddings
            similarities = []
            for i, item in enumerate(self.embeddings_data):
                sim = cosine_similarity(
                    query_vector.reshape(1, -1),
                    item["embedding"].reshape(1, -1)
                )[0][0]
                similarities.append((i, sim))

            # Sort by similarity and take top_k
            similarities.sort(key=lambda x: x[1], reverse=True)
            top_results = similarities[:top_k]

            results = []
            for idx, score in top_results:
                item = self.embeddings_data[idx]
                results.append({
                    "content": item["content"],
                    "similarity_score": float(score),
                    "source_kind": item["source_kind"],
                    "source_id": item["source_id"],
                    "ontology_class_id": item.get("ontology_class_id")
                })

            return results

        except Exception as e:
            logger.error("Semantic search failed", error=str(e))
            return []
    
    def generate_interactive_visualization(self, output_path: str = "static/knowledge_graph.html"):
        """Generate interactive graph visualization using pyvis"""
        try:
            net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white")
            net.from_nx(self.graph)
            
            # Customize visualization
            net.set_options("""
            var options = {
              "physics": {
                "enabled": true,
                "stabilization": {"iterations": 100}
              },
              "interaction": {
                "hover": true,
                "tooltipDelay": 200
              }
            }
            """)
            
            net.save_graph(output_path)
            logger.info(f"Interactive graph saved to {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error("Failed to generate visualization", error=str(e))
            return None
