from typing import List, Dict, Any
import sqlalchemy as sa
from sqlalchemy import MetaData, inspect
import json

class SQLSchemaLoader:
    def __init__(self, connection_string: str):
        """Initialize the SQL Schema Loader with a database connection string."""
        self.engine = sa.create_engine(connection_string)
        self.metadata = MetaData()
        self.inspector = inspect(self.engine)
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get schema information for a specific table."""
        columns = self.inspector.get_columns(table_name)
        pk = self.inspector.get_pk_constraint(table_name)
        fks = self.inspector.get_foreign_keys(table_name)
        
        return {
            "table_name": table_name,
            "columns": [
                {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"],
                    "primary_key": col["name"] in pk["constrained_columns"] if pk else False
                }
                for col in columns
            ],
            "primary_keys": pk["constrained_columns"] if pk else [],
            "foreign_keys": [
                {
                    "referred_table": fk["referred_table"],
                    "constrained_columns": fk["constrained_columns"],
                    "referred_columns": fk["referred_columns"]
                }
                for fk in fks
            ]
        }
    
    def create_schema_document(self, table_name: str) -> Dict[str, Any]:
        """Create a document from table schema for vector storage."""
        schema = self.get_table_schema(table_name)
        
        # Create a natural language description of the table
        description = f"Table '{table_name}' with columns: "
        column_descriptions = []
        
        for col in schema["columns"]:
            desc = f"{col['name']} ({col['type']})"
            if col['primary_key']:
                desc += " (Primary Key)"
            if not col['nullable']:
                desc += " (Required)"
            column_descriptions.append(desc)
        
        description += ", ".join(column_descriptions)
        
        if schema["foreign_keys"]:
            description += "\nRelationships: "
            for fk in schema["foreign_keys"]:
                description += f"\n- References {fk['referred_table']} through columns {fk['constrained_columns']}"
        
        return {
            "text": description,
            "metadata": {
                "table_name": table_name,
                "schema": schema
            }
        }
    
    def load_all_schemas(self) -> List[Dict[str, Any]]:
        """Load schemas for all tables in the database."""
        table_names = self.inspector.get_table_names()
        return [self.create_schema_document(table_name) for table_name in table_names]