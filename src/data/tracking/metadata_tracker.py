from datetime import datetime
from typing import Dict, Any
import json
import os

class MetadataTracker:
    """Tracks metadata for educational resources"""
    
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.metadata_path = os.path.join(base_path, "metadata")
        os.makedirs(self.metadata_path, exist_ok=True)
    
    def record_source(self, resource_id: str, source_info: Dict[str, Any]):
        """Record source information for a resource"""
        metadata = {
            "resource_id": resource_id,
            "source": source_info,
            "collection_date": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "validation_status": "pending"
        }
        
        file_path = os.path.join(self.metadata_path, f"{resource_id}_metadata.json")
        with open(file_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def update_validation_status(self, resource_id: str, status: str):
        """Update validation status of a resource"""
        file_path = os.path.join(self.metadata_path, f"{resource_id}_metadata.json")
        with open(file_path, 'r') as f:
            metadata = json.load(f)
        
        metadata["validation_status"] = status
        metadata["last_updated"] = datetime.now().isoformat()
        
        with open(file_path, 'w') as f:
            json.dump(metadata, f, indent=2) 