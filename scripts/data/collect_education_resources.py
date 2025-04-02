#!/usr/bin/env python3

import argparse
import logging
from pathlib import Path
from src.data.collectors import (
    CurriculumCollector,
    ScenarioCollector,
    InteractionCollector
)
from src.data.tracking import MetadataTracker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_argparse():
    parser = argparse.ArgumentParser(description='Collect educational resources')
    parser.add_argument('--type', choices=['curriculum', 'scenarios', 'interactions'],
                       required=True, help='Type of data to collect')
    parser.add_argument('--grade-level', help='Grade level to collect')
    parser.add_argument('--subject', help='Subject area to collect')
    return parser

def main():
    parser = setup_argparse()
    args = parser.parse_args()
    
    base_path = Path(__file__).parent.parent.parent
    data_path = base_path / 'data'
    
    metadata_tracker = MetadataTracker(str(data_path))
    
    collectors = {
        'curriculum': CurriculumCollector,
        'scenarios': ScenarioCollector,
        'interactions': InteractionCollector
    }
    
    collector_class = collectors[args.type]
    collector = collector_class(
        grade_level=args.grade_level,
        subject=args.subject
    )
    
    try:
        logger.info(f"Starting collection of {args.type} data")
        collected_data = collector.collect()
        
        # Record metadata
        metadata_tracker.record_source(
            collected_data['id'],
            {
                'type': args.type,
                'grade_level': args.grade_level,
                'subject': args.subject
            }
        )
        
        logger.info(f"Successfully collected {args.type} data")
    except Exception as e:
        logger.error(f"Error collecting {args.type} data: {str(e)}")
        raise

if __name__ == '__main__':
    main() 