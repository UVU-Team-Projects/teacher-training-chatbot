from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List

class BaseDataCollector(ABC):
    """Base class for all data collectors in the system."""
    
    def __init__(self):
        self.metadata = {
            "collection_date": None,
            "last_updated": None,
            "validation_status": "pending",
            "source": None
        }
    
    @abstractmethod
    def collect(self) -> Dict[str, Any]:
        """Main collection method to be implemented by specific collectors"""
        pass
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Basic validation of collected data"""
        self.metadata["last_updated"] = datetime.now()
        return True
    
    def add_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Adds standard metadata to collected data"""
        return {
            **data,
            "metadata": self.metadata
        } 