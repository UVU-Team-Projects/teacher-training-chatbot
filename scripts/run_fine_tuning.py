#!/usr/bin/env python3

import argparse
import json
import logging
import os
from ai.dataset_preparation import DatasetPreparator
from ai.fine_tuning import ModelFineTuner
from ai.model_evaluation import ModelEvaluator
from config.settings import DEBUG

# Setup logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/fine_tuning.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_scenarios(file_path):
    """Load teaching scenarios from JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading scenarios from {file_path}: {str(e)}")
        raise

def run_fine_tuning(args):
    """Run the fine-tuning pipeline"""
    try:
        # Load scenarios
        logger.info(f"Loading scenarios from {args.train_data}")
        scenarios = load_scenarios(args.train_data)
        
        # Prepare dataset
        logger.info("Preparing training dataset...")
        preparator = DatasetPreparator()
        df = preparator.prepare_training_data(scenarios)
        
        # Validate dataset
        if not preparator.validate_dataset(df):
            logger.error("Dataset validation failed!")
            return
        
        # Split dataset
        train_size = int(len(df) * 0.8)
        train_data = df[:train_size]
        val_data = df[train_size:]
        
        logger.info(f"Training data size: {len(train_data)}")
        logger.info(f"Validation data size: {len(val_data)}")
        
        # Initialize fine-tuner
        logger.info("Initializing model fine-tuner...")
        fine_tuner = ModelFineTuner(
            model_name=args.base_model
        )
        
        # Prepare model
        logger.info("Preparing model for fine-tuning...")
        fine_tuner.prepare_model()
        
        # Run fine-tuning
        logger.info(f"Starting fine-tuning for {args.num_epochs} epochs...")
        fine_tuner.train(
            train_dataset=train_data,
            validation_dataset=val_data,
            output_dir=args.output_dir,
            num_epochs=args.num_epochs
        )
        
        # Evaluate model
        logger.info("Evaluating fine-tuned model...")
        evaluator = ModelEvaluator()
        
        # Generate predictions for test set
        predictions = []
        ground_truth = val_data['response'].tolist()
        
        for query in val_data['instruction']:
            response = fine_tuner.model.generate(query)
            predictions.append(response)
        
        # Calculate metrics
        metrics = evaluator.evaluate_responses(predictions, ground_truth)
        
        # Log results
        logger.info("Evaluation Results:")
        logger.info(f"Average Similarity: {metrics['average_similarity']:.4f}")
        logger.info(f"Min Similarity: {metrics['min_similarity']:.4f}")
        logger.info(f"Max Similarity: {metrics['max_similarity']:.4f}")
        logger.info(f"Std Similarity: {metrics['std_similarity']:.4f}")
        
        # Save metrics
        metrics_file = os.path.join(args.output_dir, 'metrics.json')
        with open(metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        logger.info(f"Fine-tuning completed! Model saved to {args.output_dir}")
        
    except Exception as e:
        logger.error(f"Error during fine-tuning: {str(e)}")
        raise

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Run the fine-tuning pipeline')
    parser.add_argument('--train_data', required=True,
                      help='Path to training data JSON file')
    parser.add_argument('--output_dir', required=True,
                      help='Directory to save fine-tuned model')
    parser.add_argument('--base_model', default="meta-llama/Llama-2-7b",
                      help='Base model to fine-tune')
    parser.add_argument('--num_epochs', type=int, default=3,
                      help='Number of training epochs')
    parser.add_argument('--debug', action='store_true',
                      help='Enable debug mode')
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    run_fine_tuning(args)

if __name__ == "__main__":
    main() 