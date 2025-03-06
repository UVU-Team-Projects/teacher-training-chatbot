from typing import Dict, Any
import yaml
from .collectors import ScenarioCollector, TeacherInteractionCollector
from .processors import ScenarioProcessor, InteractionProcessor

class DataCollectionOrchestrator:
    """Orchestrates the data collection process for UTAH-TTA"""
    
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.collectors = {
            "scenario": ScenarioCollector(self.config["collectors"]["scenario"]),
            "interaction": TeacherInteractionCollector(self.config["collectors"]["interaction"])
        }
        
        self.processors = {
            "scenario": ScenarioProcessor(self.config["processing"]),
            "interaction": InteractionProcessor(self.config["processing"])
        }
    
    def collect_and_process(self, data_type: str) -> Dict[str, Any]:
        """Collect and process specific type of data"""
        if data_type not in self.collectors:
            raise ValueError(f"Unknown data type: {data_type}")
        
        collector = self.collectors[data_type]
        processor = self.processors[data_type]
        
        raw_data = collector.collect()
        processed_data = processor.process(raw_data)
        
        self._store_data(processed_data, data_type)
        return processed_data
    
    def _store_data(self, data: Dict[str, Any], data_type: str):
        """Store processed data with appropriate privacy controls"""
        # Implementation for secure data storage
        pass 