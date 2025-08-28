#!/usr/bin/env python3
"""
Real Google LangExtract Integration for Ontology Extension
Processes any document type and converts output to ontology suggestions
"""

import os
import json
import uuid
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import tempfile
import mimetypes
from pathlib import Path

# LangExtract imports
import langextract
from langextract import extract
from langextract.data import ExampleData, Extraction

# Pydantic for data validation
from pydantic import BaseModel, Field

class OntologyClass(BaseModel):
    """Ontology class extracted from document"""
    id: str
    label: str
    type: str
    confidence: float = Field(ge=0.0, le=1.0)
    properties: Dict[str, Any] = {}
    source_text: Optional[str] = None
    context: Optional[str] = None

class OntologyRelation(BaseModel):
    """Ontology relation extracted from document"""
    id: str
    subject_class_id: str
    predicate: str
    object_class_id: str
    confidence: float = Field(ge=0.0, le=1.0)
    properties: Dict[str, Any] = {}
    source_text: Optional[str] = None

class ExtractionResult(BaseModel):
    """Complete extraction result from LangExtract"""
    document_id: str
    source_filename: str
    extraction_timestamp: datetime
    langextract_version: str
    classes: List[OntologyClass]
    relations: List[OntologyRelation]
    raw_langextract_output: Dict[str, Any]
    processing_stats: Dict[str, Any]

class LangExtractOntologyProcessor:
    """
    Real LangExtract integration for ontology extension
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with LangExtract configuration"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("LANGEXTRACT_API_KEY")

        # For now, we'll use the basic extract function without examples
        self.examples = []

        # Ontology-specific extraction prompt
        self.extraction_prompt = """
        Extract structured business information from this document to extend a financial ontology.

        Focus on identifying:
        1. **Business Entities**: Companies, departments, roles, systems, accounts, processes
        2. **Data Sources**: Software systems, databases, files, reports, APIs
        3. **Business Processes**: Workflows, procedures, operations, activities
        4. **Relationships**: How entities connect and interact with each other
        5. **Financial Concepts**: Account types, financial instruments, metrics, KPIs

        For each entity, provide:
        - name: Clear, descriptive name
        - type: Category (BusinessProcess, DataSource, Role, Account, System, etc.)
        - description: Brief explanation of what it is
        - confidence: How confident you are (0.0-1.0)
        - properties: Additional relevant attributes

        For relationships, provide:
        - subject: The entity that performs the action
        - predicate: The relationship type (uses, manages, reports_to, contains, etc.)
        - object: The entity being acted upon
        - confidence: How confident you are (0.0-1.0)
        """
    
    async def process_document(self, 
                             file_path: str, 
                             filename: str,
                             domain: str = "default") -> ExtractionResult:
        """
        Process any document type with real LangExtract
        """
        document_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Detect file type and prepare for extraction
            mime_type, _ = mimetypes.guess_type(file_path)
            file_size = os.path.getsize(file_path)
            
            print(f"🔍 Processing {filename} ({mime_type}, {file_size} bytes)")

            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_content = f.read()

            # Create example data for LangExtract
            example_data = ExampleData(
                text="Sales Revenue: $150,000. Operating Expenses: $45,000. Acme Corporation profit and loss statement.",
                extractions=[
                    Extraction(
                        extraction_text="Sales Revenue",
                        extraction_class="FinancialAccount",
                        description="Revenue account for sales income"
                    ),
                    Extraction(
                        extraction_text="Operating Expenses",
                        extraction_class="ExpenseAccount",
                        description="Account for operational costs"
                    ),
                    Extraction(
                        extraction_text="Acme Corporation",
                        extraction_class="Organization",
                        description="Company entity"
                    )
                ]
            )

            # Use real LangExtract to process the document
            print(f"🧠 Calling LangExtract API...")
            annotated_doc = extract(
                text_or_documents=file_content,
                prompt_description=self.extraction_prompt,
                examples=[example_data],
                api_key=self.api_key,
                model_id="gpt-4o-mini",  # or "gemini-1.5-flash"
                temperature=0.1,
                max_char_buffer=8000,
                debug=True
            )

            # Extract the structured data from LangExtract result
            print(f"📊 LangExtract returned: {type(annotated_doc)}")

            # Process LangExtract results
            raw_result = {"entities": [], "relationships": []}

            if hasattr(annotated_doc, 'extractions'):
                for extraction in annotated_doc.extractions:
                    entity = {
                        "name": extraction.extraction_text,
                        "type": extraction.extraction_class,
                        "description": extraction.description or "",
                        "confidence": 0.8,  # Default confidence
                        "source_text": extraction.extraction_text
                    }
                    raw_result["entities"].append(entity)

            print(f"📋 Processed {len(raw_result.get('entities', []))} entities from LangExtract")
            
            # Convert LangExtract output to ontology classes and relations
            classes = []
            relations = []
            
            # Process entities
            if "entities" in raw_result:
                for entity in raw_result["entities"]:
                    ontology_class = OntologyClass(
                        id=f"{domain}_{entity['name'].lower().replace(' ', '_')}",
                        label=entity["name"],
                        type=f"pl:{entity.get('type', 'Entity')}",
                        confidence=entity.get("confidence", 0.8),
                        properties={
                            "description": entity.get("description", ""),
                            "domain": domain,
                            "extracted_from": filename,
                            **entity.get("properties", {})
                        },
                        source_text=entity.get("source_text", ""),
                        context=f"Extracted from {filename}"
                    )
                    classes.append(ontology_class)
            
            # Process relationships
            if "relationships" in raw_result:
                for rel in raw_result["relationships"]:
                    relation = OntologyRelation(
                        id=str(uuid.uuid4()),
                        subject_class_id=f"{domain}_{rel['subject'].lower().replace(' ', '_')}",
                        predicate=rel["predicate"],
                        object_class_id=f"{domain}_{rel['object'].lower().replace(' ', '_')}",
                        confidence=rel.get("confidence", 0.8),
                        properties={
                            "domain": domain,
                            "extracted_from": filename
                        },
                        source_text=rel.get("source_text", "")
                    )
                    relations.append(relation)
            
            # Process procedures as special entity types
            if "procedures" in raw_result:
                for proc in raw_result["procedures"]:
                    procedure_class = OntologyClass(
                        id=f"{domain}_procedure_{proc['name'].lower().replace(' ', '_')}",
                        label=proc["name"],
                        type="pl:BusinessProcess",
                        confidence=0.85,
                        properties={
                            "description": f"Business procedure: {proc['name']}",
                            "steps": proc.get("steps", []),
                            "inputs": proc.get("inputs", []),
                            "outputs": proc.get("outputs", []),
                            "roles": proc.get("roles", []),
                            "domain": domain,
                            "extracted_from": filename
                        },
                        context=f"Business procedure extracted from {filename}"
                    )
                    classes.append(procedure_class)
            
            # Process data sources
            if "data_sources" in raw_result:
                for ds in raw_result["data_sources"]:
                    data_source_class = OntologyClass(
                        id=f"{domain}_datasource_{ds['name'].lower().replace(' ', '_')}",
                        label=ds["name"],
                        type="pl:DataSource",
                        confidence=0.8,
                        properties={
                            "description": f"Data source: {ds['name']}",
                            "source_type": ds.get("type", ""),
                            "format": ds.get("format", ""),
                            "access_method": ds.get("access_method", ""),
                            "frequency": ds.get("frequency", ""),
                            "domain": domain,
                            "extracted_from": filename
                        },
                        context=f"Data source extracted from {filename}"
                    )
                    classes.append(data_source_class)
            
            # Create extraction result
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = ExtractionResult(
                document_id=document_id,
                source_filename=filename,
                extraction_timestamp=start_time,
                langextract_version=getattr(langextract, '__version__', '1.0.0'),
                classes=classes,
                relations=relations,
                raw_langextract_output=raw_result,
                processing_stats={
                    "processing_time_seconds": processing_time,
                    "file_size_bytes": file_size,
                    "mime_type": mime_type,
                    "classes_extracted": len(classes),
                    "relations_extracted": len(relations)
                }
            )
            
            print(f"✅ Extracted {len(classes)} classes and {len(relations)} relations in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            # Return minimal result on error
            return ExtractionResult(
                document_id=document_id,
                source_filename=filename,
                extraction_timestamp=start_time,
                langextract_version=getattr(langextract, '__version__', '1.0.0'),
                classes=[],
                relations=[],
                raw_langextract_output={"error": str(e)},
                processing_stats={
                    "processing_time_seconds": (datetime.now() - start_time).total_seconds(),
                    "error": str(e)
                }
            )

# Global processor instance
langextract_processor = None

def get_langextract_processor() -> LangExtractOntologyProcessor:
    """Get or create LangExtract processor instance"""
    global langextract_processor
    if langextract_processor is None:
        langextract_processor = LangExtractOntologyProcessor()
    return langextract_processor

async def process_document_with_langextract(file_path: str, filename: str, domain: str = "default") -> ExtractionResult:
    """
    Main function to process documents with real LangExtract
    """
    processor = get_langextract_processor()
    return await processor.process_document(file_path, filename, domain)
