# app/services/schema_registry.py
import importlib
import pkgutil
from typing import Dict, Type, List, Any
from pathlib import Path

from ..models.base import BaseExtractionSchema
from ..utils.logging_manager import LoggingManager

logger = LoggingManager.get_logger(__name__)

class SchemaRegistry:
    """Auto-discovery registry for extraction schemas"""
    
    _schemas: Dict[str, Type[BaseExtractionSchema]] = {}
    _discovered = False
    
    @classmethod
    def discover_schemas(cls) -> None:
        """Automatically discover all schema classes"""
        if cls._discovered:
            return
            
        logger.info("Discovering extraction schemas...")
        
        # Get the schemas package path
        schemas_path = Path(__file__).parent.parent / "models" / "schemas"
        
        # Import all modules in the schemas package
        for module_info in pkgutil.iter_modules([str(schemas_path)]):
            if module_info.name.startswith('_'):
                continue
                
            try:
                module_name = f"app.models.schemas.{module_info.name}"
                module = importlib.import_module(module_name)
                
                # Find all BaseExtractionSchema subclasses in the module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    
                    if (isinstance(attr, type) and 
                        issubclass(attr, BaseExtractionSchema) and 
                        attr != BaseExtractionSchema and
                        hasattr(attr, 'extraction_type') and
                        attr.extraction_type):
                        
                        extraction_type = attr.extraction_type
                        cls._schemas[extraction_type] = attr
                        logger.info(f"Discovered schema: {extraction_type} -> {attr.__name__}")
                        
            except Exception as e:
                logger.warning(f"Failed to load schema module {module_info.name}: {e}")
        
        cls._discovered = True
        logger.info(f"Schema discovery complete. Found {len(cls._schemas)} schemas.")
    
    @classmethod
    def get_schema(cls, extraction_type: str) -> Type[BaseExtractionSchema]:
        """Get schema class for extraction type"""
        cls.discover_schemas()
        
        if extraction_type not in cls._schemas:
            available = list(cls._schemas.keys())
            raise ValueError(f"Unknown extraction type: {extraction_type}. Available: {available}")
        
        return cls._schemas[extraction_type]
    
    @classmethod
    def get_all_schemas(cls) -> Dict[str, Dict[str, Any]]:
        """Get information about all available schemas"""
        cls.discover_schemas()
        
        result = {}
        for extraction_type, schema_class in cls._schemas.items():
            result[extraction_type] = {
                "name": extraction_type,
                "description": schema_class.description,
                "prompt": schema_class.prompt,
                "schema": schema_class.model_json_schema(),
                "class_name": schema_class.__name__
            }
        return result
    
    @classmethod
    def get_available_types(cls) -> List[str]:
        """Get list of available extraction types"""
        cls.discover_schemas()
        return list(cls._schemas.keys())
    
    @classmethod
    def reload_schemas(cls) -> None:
        """Force reload of all schemas (useful for development)"""
        cls._schemas.clear()
        cls._discovered = False
        cls.discover_schemas()