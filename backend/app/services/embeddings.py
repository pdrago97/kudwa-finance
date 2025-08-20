import os
from openai import OpenAI
from typing import List

class EmbeddingService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key.startswith("sk-placeholder"):
            print(f"Warning: OPENAI_API_KEY not properly set (current: {api_key[:20] if api_key else 'None'}...)")
            self.client = None
            self.model = None
        else:
            self.client = OpenAI(api_key=api_key)
            self.model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for a list of texts"""
        if not texts or not self.client:
            return []

        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )

        return [embedding.embedding for embedding in response.data]
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at word boundary
            if end < len(text):
                last_space = chunk.rfind(' ')
                if last_space > chunk_size // 2:
                    chunk = chunk[:last_space]
                    end = start + last_space
            
            chunks.append(chunk.strip())
            start = end - overlap
            
            if start >= len(text):
                break
        
        return chunks

# Global instance
embedding_service = EmbeddingService()
