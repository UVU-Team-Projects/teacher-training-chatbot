#!/usr/bin/env python3

import argparse
import logging
from pathlib import Path
from src.data.validators import (
    CurriculumValidator,
    ScenarioValidator,
    InteractionValidator
)
from src.data.tracking import MetadataTracker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_resource(resource_path: Path, resource_type: str, metadata_tracker: MetadataTracker):
    """Validate a specific resource"""
    validators = {
        'curriculum': CurriculumValidator(),
        'scenarios': ScenarioValidator(),
        'interactions': InteractionValidator()
    }
    
    validator = validators[resource_type]
    
    try:
        is_valid = validator.validate(resource_path)
        status = "validated" if is_valid else "failed_validation"
        metadata_tracker.update_validation_status(resource_path.stem, status)
        return is_valid
    except Exception as e:
        logger.error(f"Validation error for {resource_path}: {str(e)}")
        metadata_tracker.update_validation_status(resource_path.stem, "validation_error")
        return False

def main():
    parser = argparse.ArgumentParser(description='Validate educational content')
    parser.add_argument('--type', choices=['curriculum', 'scenarios', 'interactions'],
                       required=True, help='Type of content to validate')
    parser.add_argument('--path', required=True, help='Path to content directory')
    args = parser.parse_args()
    
    base_path = Path(__file__).parent.parent.parent
    metadata_tracker = MetadataTracker(str(base_path / 'data'))
    
    content_path = Path(args.path)
    if not content_path.exists():
        logger.error(f"Path does not exist: {content_path}")
        return
    
    logger.info(f"Starting validation of {args.type} content in {content_path}")
    
    for resource_file in content_path.glob('**/*.*'):
        if validate_resource(resource_file, args.type, metadata_tracker):
            logger.info(f"Validated: {resource_file}")
        else:
            logger.warning(f"Validation failed: {resource_file}")

if __name__ == '__main__':
    main() 