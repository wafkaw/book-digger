"""
Main entry point for Kindle Reading Assistant
"""
import os
import json
import logging
from typing import List, Dict, Any
from pathlib import Path

from src.data_collection.kindle_parser import KindleParser
from src.knowledge_graph.ai_analysis import AIAnalysisInterface
from src.output.obsidian_generator import ObsidianGenerator


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('kindle_assistant.log'),
            logging.StreamHandler()
        ]
    )


def main():
    """Main function to run the Kindle Reading Assistant"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Initialize components
    parser = KindleParser()
    ai_interface = AIAnalysisInterface(mock_mode=True)
    obsidian_generator = ObsidianGenerator()
    
    logger.info("Kindle Reading Assistant started")
    
    # Process materials directory
    material_dir = Path("material")
    if not material_dir.exists():
        logger.error(f"Material directory not found: {material_dir}")
        return
    
    # Find all HTML files
    html_files = list(material_dir.glob("*.html"))
    if not html_files:
        logger.warning("No HTML files found in material directory")
        return
    
    logger.info(f"Found {len(html_files)} HTML files to process")
    
    # Process each file
    all_results = []
    for html_file in html_files:
        try:
            logger.info(f"Processing {html_file.name}")
            
            # Parse HTML file
            book = parser.parse_file(str(html_file))
            
            # Analyze content
            analysis_result = ai_interface.analyze_book(book)
            all_results.append(analysis_result)
            
            # Generate Obsidian files
            obsidian_generator.generate_book_files(book, analysis_result)
            
            logger.info(f"Successfully processed {html_file.name}")
            
        except Exception as e:
            logger.error(f"Error processing {html_file.name}: {e}")
            continue
    
    # Generate summary report
    if all_results:
        generate_summary_report(all_results)
    
    logger.info("Processing completed")


def generate_summary_report(results: List[Dict[str, Any]]):
    """Generate a summary report of all processed books"""
    report = {
        "total_books": len(results),
        "total_highlights": sum(len(r["analysis_results"]) for r in results),
        "books_processed": [r["book"]["metadata"]["title"] for r in results],
        "processing_date": str(Path().cwd())
    }
    
    with open("processing_summary.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"Processed {len(results)} books with {report['total_highlights']} total highlights")


if __name__ == "__main__":
    main()