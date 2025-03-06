#!/usr/bin/env python3

import asyncio
import logging
import argparse
from ai.rag_pipeline import RAGPipeline
from monitoring.performance_monitor import start_monitoring
from config.settings import DEBUG

# Setup logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/rag_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def run_service(args):
    """Run the RAG service"""
    try:
        # Start monitoring if enabled
        if args.monitor:
            start_monitoring()
            logger.info("Monitoring started on port 8000")
        
        # Initialize RAG pipeline
        logger.info("Initializing RAG pipeline...")
        pipeline = RAGPipeline()
        
        # Example queries for testing
        test_queries = [
            "How to handle classroom disruption?",
            "What are effective teaching strategies?",
            "How to engage students in online learning?"
        ]
        
        # Process test queries
        logger.info("Processing test queries...")
        for query in test_queries:
            try:
                result = await pipeline.process_query(query)
                logger.info(f"Query: {query}")
                logger.info(f"Response: {result['response']}")
                logger.info(f"Sources: {result['sources']}")
                logger.info("-" * 50)
            except Exception as e:
                logger.error(f"Error processing query '{query}': {str(e)}")
        
        # Keep service running
        logger.info("RAG service is running. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down RAG service...")
    except Exception as e:
        logger.error(f"Error running RAG service: {str(e)}")
        raise

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Run the RAG service')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--monitor', action='store_true', help='Enable monitoring')
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    asyncio.run(run_service(args))

if __name__ == "__main__":
    main() 