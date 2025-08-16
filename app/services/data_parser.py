"""
Advanced data parsing service for multiple financial data formats
Handles QuickBooks P&L reports and Rootfi API data
"""

import json
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date
import structlog
from decimal import Decimal

from app.services.supabase_client import supabase_service

logger = structlog.get_logger(__name__)


class FinancialDataParser:
    """Advanced parser for financial data with intelligent entity extraction"""
    
    def __init__(self):
        self.supported_formats = ["quickbooks_pl", "rootfi_api", "generic_json"]

    async def _create_kudwa_entity(
        self,
        entity_type: str,
        name: str,
        properties: Dict[str, Any],
        document_id: Optional[str] = None,
        confidence_score: float = 0.9
    ) -> Dict[str, Any]:
        """Create entity using Kudwa ontology system"""
        import uuid

        # First, ensure the ontology class exists
        class_result = supabase_service.client.table("kudwa_ontology_classes").select("*").eq("class_id", entity_type).execute()

        if not class_result.data:
            # Create the ontology class
            supabase_service.client.table("kudwa_ontology_classes").insert({
                "id": str(uuid.uuid4()),
                "domain": "financial",
                "class_id": entity_type,
                "label": entity_type.replace("_", " ").title(),
                "class_type": "entity",
                "properties": {
                    "auto_generated": True,
                    "source": "rootfi_parser",
                    "description": f"Auto-generated class for {entity_type}"
                },
                "confidence_score": 0.9,
                "status": "pending_review"
            }).execute()

        # Get or create dataset for this document
        dataset_id = await self._get_or_create_dataset(document_id, properties)

        # Create financial observation
        observation_id = str(uuid.uuid4())
        observation_data = {
            "id": observation_id,
            "dataset_id": dataset_id,
            "source_document_id": document_id,
            "observation_type": entity_type,
            "account_name": name,
            "amount": properties.get("amount", 0),
            "currency": properties.get("currency", "USD"),
            "metadata": {
                "properties": properties,
                "confidence_score": confidence_score,
                "created_by": "rootfi_parser"
            }
        }

        # Add period information if available
        if "period_start" in properties:
            observation_data["period_start"] = properties["period_start"]
        if "period_end" in properties:
            observation_data["period_end"] = properties["period_end"]

        # Add account_id (required field)
        observation_data["account_id"] = properties.get("account_id", f"auto_{entity_type}_{observation_id[:8]}")

        result = supabase_service.client.table("kudwa_financial_observations").insert(observation_data).execute()

        return {
            "id": observation_id,
            "entity_type": entity_type,
            "name": name,
            "properties": properties
        }

    async def _get_or_create_dataset(
        self,
        document_id: Optional[str],
        properties: Dict[str, Any]
    ) -> str:
        """Get or create a dataset for the document"""
        import uuid

        # Check if dataset already exists for this document
        if document_id:
            existing_dataset = supabase_service.client.table("kudwa_financial_datasets").select("id").eq("source_document_id", document_id).execute()
            if existing_dataset.data:
                return existing_dataset.data[0]["id"]

        # Create new dataset
        dataset_id = str(uuid.uuid4())
        dataset_data = {
            "id": dataset_id,
            "name": f"RootFi Financial Data - {properties.get('period_start', 'Unknown')}",
            "description": f"Financial data imported from RootFi API for period {properties.get('period_start')} to {properties.get('period_end')}",
            "source_document_id": document_id,
            "period_start": properties.get("period_start"),
            "period_end": properties.get("period_end"),
            "currency": properties.get("currency", "USD"),
            "created_by": "rootfi_parser"
        }

        supabase_service.client.table("kudwa_financial_datasets").insert(dataset_data).execute()
        return dataset_id
        
    async def parse_financial_data(
        self,
        data: Dict[str, Any],
        source_format: str,
        document_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Main parsing method that routes to specific parsers"""
        try:
            logger.info(
                "Starting financial data parsing",
                source_format=source_format,
                document_id=document_id
            )
            
            if source_format == "quickbooks_pl":
                return await self._parse_quickbooks_pl(data, document_id)
            elif source_format == "rootfi_api":
                return await self._parse_rootfi_data(data, document_id)
            else:
                return await self._parse_generic_financial(data, document_id)
                
        except Exception as e:
            logger.error(
                "Financial data parsing failed",
                source_format=source_format,
                error=str(e)
            )
            raise
    
    async def _parse_quickbooks_pl(
        self,
        data: Dict[str, Any],
        document_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Parse QuickBooks Profit & Loss report format"""
        
        # Extract header information
        header = data.get("data", {}).get("Header", {})
        report_info = {
            "report_name": header.get("ReportName"),
            "report_basis": header.get("ReportBasis"),
            "start_period": header.get("StartPeriod"),
            "end_period": header.get("EndPeriod"),
            "currency": header.get("Currency"),
            "accounting_standard": self._extract_option_value(header.get("Option", []), "AccountingStandard")
        }
        
        # Extract time periods from columns
        columns = data.get("data", {}).get("Columns", {}).get("Column", [])
        time_periods = self._extract_time_periods(columns)
        
        # Parse financial data rows
        rows = data.get("data", {}).get("Rows", {}).get("Row", [])
        financial_entities = await self._parse_quickbooks_rows(rows, time_periods, document_id)
        
        # Create company entity
        company_entity = await self._create_company_entity(report_info, document_id)
        
        return {
            "source_format": "quickbooks_pl",
            "report_info": report_info,
            "time_periods": time_periods,
            "company_entity": company_entity,
            "financial_entities": financial_entities,
            "total_entities_extracted": len(financial_entities) + 1,
            "parsing_metadata": {
                "parser_version": "1.0",
                "parsing_timestamp": datetime.now().isoformat(),
                "data_quality_score": self._calculate_data_quality(financial_entities)
            }
        }
    
    async def _parse_rootfi_data(
        self,
        data: Dict[str, Any],
        document_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Parse Rootfi API financial data format with comprehensive entity extraction"""

        financial_entities = []

        # Process each data record
        for record in data.get("data", []):
            # Extract company information
            company_entity = await self._create_rootfi_company_entity(record, document_id)
            financial_entities.append(company_entity)

            # Extract revenue entities with detailed line items
            revenue_entities = await self._parse_rootfi_revenue(record, document_id)
            financial_entities.extend(revenue_entities)

            # Extract expense entities with detailed line items
            expense_entities = await self._parse_rootfi_expenses(record, document_id)
            financial_entities.extend(expense_entities)

            # Extract cost of goods sold entities
            cogs_entities = await self._parse_rootfi_cogs(record, document_id)
            financial_entities.extend(cogs_entities)

            # Extract non-operating revenue and expenses
            non_op_entities = await self._parse_rootfi_non_operating(record, document_id)
            financial_entities.extend(non_op_entities)

            # Create financial summary entity
            summary_entity = await self._create_financial_summary_entity(record, document_id)
            financial_entities.append(summary_entity)

            # Create period entity for time-based analysis
            period_entity = await self._create_period_entity(record, document_id)
            financial_entities.append(period_entity)

        return {
            "source_format": "rootfi_api",
            "financial_entities": financial_entities,
            "total_entities_extracted": len(financial_entities),
            "parsing_metadata": {
                "parser_version": "2.0",
                "parsing_timestamp": datetime.now().isoformat(),
                "records_processed": len(data.get("data", [])),
                "entity_types_extracted": ["company", "revenue", "expense", "cogs", "non_operating", "summary", "period"],
                "data_quality_score": self._calculate_data_quality(financial_entities)
            }
        }
    
    async def _parse_quickbooks_rows(
        self,
        rows: List[Dict],
        time_periods: List[Dict],
        document_id: Optional[str]
    ) -> List[Dict]:
        """Parse QuickBooks row data into financial entities"""
        
        entities = []
        
        for row in rows:
            if "Header" in row:
                # This is a category header (Income, Expenses, etc.)
                category_name = self._extract_row_value(row["Header"]["ColData"], 0)
                
                if "Rows" in row and "Row" in row["Rows"]:
                    # Process sub-rows for this category
                    sub_entities = await self._parse_quickbooks_sub_rows(
                        row["Rows"]["Row"],
                        category_name,
                        time_periods,
                        document_id
                    )
                    entities.extend(sub_entities)
            
            elif "ColData" in row:
                # This is a data row
                account_name = self._extract_row_value(row["ColData"], 0)
                if account_name and account_name not in ["", "Total"]:
                    entity = await self._create_account_entity(
                        account_name,
                        row["ColData"],
                        time_periods,
                        document_id
                    )
                    if entity:
                        entities.append(entity)
        
        return entities
    
    async def _parse_quickbooks_sub_rows(
        self,
        sub_rows: List[Dict],
        category: str,
        time_periods: List[Dict],
        document_id: Optional[str]
    ) -> List[Dict]:
        """Parse QuickBooks sub-rows recursively"""
        
        entities = []
        
        for sub_row in sub_rows:
            if "Header" in sub_row:
                account_name = self._extract_row_value(sub_row["Header"]["ColData"], 0)
                account_id = sub_row["Header"]["ColData"][0].get("id") if sub_row["Header"]["ColData"] else None
                
                # Create account entity
                entity = await self._create_account_entity(
                    account_name,
                    sub_row["Header"]["ColData"],
                    time_periods,
                    document_id,
                    category=category,
                    account_id=account_id
                )
                if entity:
                    entities.append(entity)
                
                # Process nested rows if they exist
                if "Rows" in sub_row and "Row" in sub_row["Rows"]:
                    nested_entities = await self._parse_quickbooks_sub_rows(
                        sub_row["Rows"]["Row"],
                        category,
                        time_periods,
                        document_id
                    )
                    entities.extend(nested_entities)
        
        return entities
    
    async def _parse_rootfi_revenue(
        self,
        record: Dict[str, Any],
        document_id: Optional[str]
    ) -> List[Dict]:
        """Parse Rootfi revenue data into entities"""
        
        entities = []
        
        for revenue_item in record.get("revenue", []):
            entity = await self._create_kudwa_entity(
                entity_type="revenue_stream",
                name=revenue_item.get("name", "Unknown Revenue"),
                properties={
                    "revenue_type": "business_revenue",
                    "amount": float(revenue_item.get("value", 0)),
                    "currency": "USD",
                    "period_start": record.get("period_start"),
                    "period_end": record.get("period_end"),
                    "platform_id": record.get("platform_id"),
                    "rootfi_company_id": record.get("rootfi_company_id"),
                    "line_items": revenue_item.get("line_items", []),
                    "rootfi_id": record.get("rootfi_id")
                },
                document_id=document_id,
                confidence_score=0.95
            )
            entities.append(entity)
        
        return entities
    
    async def _parse_rootfi_expenses(
        self,
        record: Dict[str, Any],
        document_id: Optional[str]
    ) -> List[Dict]:
        """Parse Rootfi expense data into entities"""
        
        entities = []
        
        for expense_item in record.get("operating_expenses", []):
            entity = await self._create_kudwa_entity(
                entity_type="expense_category",
                name=expense_item.get("name", "Unknown Expense"),
                properties={
                    "expense_type": "operating_expense",
                    "amount": float(expense_item.get("value", 0)),
                    "currency": "USD",
                    "period_start": record.get("period_start"),
                    "period_end": record.get("period_end"),
                    "platform_id": record.get("platform_id"),
                    "rootfi_company_id": record.get("rootfi_company_id"),
                    "line_items": expense_item.get("line_items", []),
                    "rootfi_id": record.get("rootfi_id")
                },
                document_id=document_id,
                confidence_score=0.95
            )
            entities.append(entity)
        
        return entities
    
    def _extract_time_periods(self, columns: List[Dict]) -> List[Dict]:
        """Extract time period information from QuickBooks columns"""
        periods = []
        
        for col in columns:
            if col.get("ColType") == "Money" and "MetaData" in col:
                metadata = {item["Name"]: item["Value"] for item in col["MetaData"]}
                if "StartDate" in metadata and "EndDate" in metadata:
                    periods.append({
                        "title": col.get("ColTitle"),
                        "start_date": metadata["StartDate"],
                        "end_date": metadata["EndDate"],
                        "col_key": metadata.get("ColKey")
                    })
        
        return periods
    
    def _extract_option_value(self, options: List[Dict], option_name: str) -> Optional[str]:
        """Extract specific option value from QuickBooks options"""
        for option in options:
            if option.get("Name") == option_name:
                return option.get("Value")
        return None
    
    def _extract_row_value(self, col_data: List[Dict], index: int) -> Optional[str]:
        """Extract value from specific column index"""
        if len(col_data) > index:
            return col_data[index].get("value")
        return None
    
    def _calculate_data_quality(self, entities: List[Dict]) -> float:
        """Calculate data quality score based on completeness and consistency"""
        if not entities:
            return 0.0
        
        total_score = 0
        for entity in entities:
            score = 0
            properties = entity.get("properties", {})
            
            # Check for required fields
            if properties.get("amount") is not None:
                score += 0.3
            if properties.get("currency"):
                score += 0.2
            if properties.get("period_start") and properties.get("period_end"):
                score += 0.3
            if entity.get("name"):
                score += 0.2
            
            total_score += score
        
        return total_score / len(entities)

    async def _create_company_entity(
        self,
        report_info: Dict[str, Any],
        document_id: Optional[str]
    ) -> Dict[str, Any]:
        """Create company entity from QuickBooks report info using Kudwa tables"""

        return await self._create_kudwa_entity(
            entity_type="company",
            name=report_info.get("company_name", "QuickBooks Company"),
            properties={
                "company_type": "reporting_entity",
                "accounting_standard": report_info.get("accounting_standard", "GAAP"),
                "report_basis": report_info.get("report_basis", "Accrual"),
                "base_currency": report_info.get("currency", "USD"),
                "reporting_period": {
                    "start": report_info.get("start_period"),
                    "end": report_info.get("end_period")
                },
                "financial_system": "QuickBooks"
            },
            document_id=document_id,
            confidence_score=0.9
        )

    async def _create_rootfi_company_entity(
        self,
        record: Dict[str, Any],
        document_id: Optional[str]
    ) -> Dict[str, Any]:
        """Create company entity from Rootfi data"""

        return await self._create_kudwa_entity(
            entity_type="company",
            name=f"Rootfi Company {record.get('rootfi_company_id')}",
            properties={
                "company_type": "api_integrated",
                "rootfi_company_id": record.get("rootfi_company_id"),
                "platform_id": record.get("platform_id"),
                "period_start": record.get("period_start"),
                "period_end": record.get("period_end"),
                "gross_profit": float(record.get("gross_profit", 0)),
                "financial_system": "Rootfi API",
                "rootfi_id": record.get("rootfi_id")
            },
            document_id=document_id,
            confidence_score=0.95
        )

    async def _create_account_entity(
        self,
        account_name: str,
        col_data: List[Dict],
        time_periods: List[Dict],
        document_id: Optional[str],
        category: Optional[str] = None,
        account_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create account entity from QuickBooks row data"""

        if not account_name or account_name in ["", "Total"]:
            return None

        # Extract time series data
        time_series_data = {}
        for i, period in enumerate(time_periods):
            if len(col_data) > i + 1:  # +1 because first column is account name
                value_str = col_data[i + 1].get("value", "0.00")
                try:
                    time_series_data[period["col_key"]] = float(value_str.replace(",", ""))
                except (ValueError, AttributeError):
                    time_series_data[period["col_key"]] = 0.0

        # Determine entity type based on category
        entity_type = "financial_account"
        if category and "income" in category.lower():
            entity_type = "revenue_account"
        elif category and any(term in category.lower() for term in ["expense", "cost"]):
            entity_type = "expense_account"

        return await self._create_kudwa_entity(
            entity_type=entity_type,
            name=account_name,
            properties={
                "account_category": category,
                "account_id": account_id,
                "time_series_data": time_series_data,
                "total_amount": sum(time_series_data.values()),
                "currency": "USD",
                "data_points": len([v for v in time_series_data.values() if v != 0])
            },
            document_id=document_id,
            confidence_score=0.9
        )

    async def _create_financial_summary_entity(
        self,
        record: Dict[str, Any],
        document_id: Optional[str]
    ) -> Dict[str, Any]:
        """Create financial summary entity from Rootfi record"""

        return await self._create_kudwa_entity(
            entity_type="financial_summary",
            name=f"Financial Summary {record.get('period_start')} to {record.get('period_end')}",
            properties={
                "summary_type": "monthly_summary",
                "period_start": record.get("period_start"),
                "period_end": record.get("period_end"),
                "gross_profit": float(record.get("gross_profit", 0)),
                "operating_profit": float(record.get("operating_profit", 0)),
                "net_profit": float(record.get("net_profit", 0)),
                "total_revenue": sum([item.get("value", 0) for item in record.get("revenue", [])]),
                "total_operating_expenses": sum([item.get("value", 0) for item in record.get("operating_expenses", [])]),
                "cost_of_goods_sold": sum([item.get("value", 0) for item in record.get("cost_of_goods_sold", [])]),
                "currency": "USD",
                "platform_id": record.get("platform_id"),
                "rootfi_id": record.get("rootfi_id")
            },
            document_id=document_id,
            confidence_score=0.95
        )

    async def _parse_rootfi_cogs(
        self,
        record: Dict[str, Any],
        document_id: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Parse cost of goods sold from Rootfi record"""
        entities = []

        for cogs_item in record.get("cost_of_goods_sold", []):
            entity = await self._create_kudwa_entity(
                entity_type="cost_of_goods_sold",
                name=cogs_item.get("name", "Unknown COGS"),
                properties={
                    "amount": float(cogs_item.get("value", 0)),
                    "period_start": record.get("period_start"),
                    "period_end": record.get("period_end"),
                    "currency": "USD",
                    "line_items_count": len(cogs_item.get("line_items", [])),
                    "rootfi_id": record.get("rootfi_id")
                },
                document_id=document_id,
                confidence_score=0.9
            )
            entities.append(entity)

            # Parse line items if present
            for line_item in cogs_item.get("line_items", []):
                line_entity = await self._create_kudwa_entity(
                    entity_type="cogs_line_item",
                    name=line_item.get("name", "Unknown Line Item"),
                    properties={
                        "amount": float(line_item.get("value", 0)),
                        "account_id": line_item.get("account_id"),
                        "parent_category": cogs_item.get("name"),
                        "parent_entity": entity["id"],
                        "period_start": record.get("period_start"),
                        "period_end": record.get("period_end"),
                        "currency": "USD"
                    },
                    document_id=document_id,
                    confidence_score=0.85
                )
                entities.append(line_entity)

        return entities

    async def _parse_rootfi_non_operating(
        self,
        record: Dict[str, Any],
        document_id: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Parse non-operating revenue and expenses from Rootfi record"""
        entities = []

        # Parse non-operating revenue
        for revenue_item in record.get("non_operating_revenue", []):
            entity = await self._create_kudwa_entity(
                entity_type="non_operating_revenue",
                name=revenue_item.get("name", "Unknown Non-Op Revenue"),
                properties={
                    "amount": float(revenue_item.get("value", 0)),
                    "period_start": record.get("period_start"),
                    "period_end": record.get("period_end"),
                    "currency": "USD",
                    "line_items_count": len(revenue_item.get("line_items", [])),
                    "rootfi_id": record.get("rootfi_id")
                },
                document_id=document_id,
                confidence_score=0.9
            )
            entities.append(entity)

        # Parse non-operating expenses
        for expense_item in record.get("non_operating_expenses", []):
            entity = await self._create_kudwa_entity(
                entity_type="non_operating_expense",
                name=expense_item.get("name", "Unknown Non-Op Expense"),
                properties={
                    "amount": float(expense_item.get("value", 0)),
                    "period_start": record.get("period_start"),
                    "period_end": record.get("period_end"),
                    "currency": "USD",
                    "line_items_count": len(expense_item.get("line_items", [])),
                    "rootfi_id": record.get("rootfi_id")
                },
                document_id=document_id,
                confidence_score=0.9
            )
            entities.append(entity)

            # Parse detailed line items for non-operating expenses
            for line_item in expense_item.get("line_items", []):
                line_entity = await self._create_kudwa_entity(
                    entity_type="non_operating_expense_line_item",
                    name=line_item.get("name", "Unknown Line Item"),
                    properties={
                        "amount": float(line_item.get("value", 0)),
                        "account_id": line_item.get("account_id"),
                        "parent_category": expense_item.get("name"),
                        "parent_entity": entity["id"],
                        "period_start": record.get("period_start"),
                        "period_end": record.get("period_end"),
                        "currency": "USD"
                    },
                    document_id=document_id,
                    confidence_score=0.85
                )
                entities.append(line_entity)

        return entities

    async def _create_period_entity(
        self,
        record: Dict[str, Any],
        document_id: Optional[str]
    ) -> Dict[str, Any]:
        """Create period entity for time-based analysis"""

        return await self._create_kudwa_entity(
            entity_type="financial_period",
            name=f"Period {record.get('period_start')} to {record.get('period_end')}",
            properties={
                "period_start": record.get("period_start"),
                "period_end": record.get("period_end"),
                "platform_id": record.get("platform_id"),
                "company_id": record.get("rootfi_company_id"),
                "period_type": "monthly",
                "currency": "USD",
                "rootfi_id": record.get("rootfi_id")
            },
            document_id=document_id,
            confidence_score=1.0
        )

    async def _parse_generic_financial(
        self,
        data: Dict[str, Any],
        document_id: Optional[str]
    ) -> Dict[str, Any]:
        """Parse generic financial JSON data"""

        # Basic entity extraction for unknown formats
        entities = []

        # Try to identify financial data patterns
        if "revenue" in data or "income" in data:
            # Handle revenue data
            pass

        if "expenses" in data or "costs" in data:
            # Handle expense data
            pass

        return {
            "source_format": "generic_json",
            "financial_entities": entities,
            "total_entities_extracted": len(entities),
            "parsing_metadata": {
                "parser_version": "1.0",
                "parsing_timestamp": datetime.now().isoformat(),
                "data_quality_score": 0.5  # Lower confidence for generic parsing
            }
        }


# Global instance
financial_parser = FinancialDataParser()
