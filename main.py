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


def setup_logging(debug_mode: bool = False):
    """Setup logging configuration with improved detail"""
    from datetime import datetime
    
    # 确保logs目录存在
    os.makedirs('logs', exist_ok=True)
    
    # 生成带时间戳的日志文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f'logs/kindle_assistant_{timestamp}.log'
    
    # 设置日志级别
    log_level = logging.DEBUG if debug_mode else logging.INFO
    
    # 创建详细的格式器
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    
    # 创建简化的控制台格式器
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 清除现有的handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # 文件处理器 - 详细日志
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # 控制台处理器 - 简化日志
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    
    # 配置根logger
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[file_handler, console_handler],
        force=True  # 强制重新配置
    )
    
    # 设置第三方库的日志级别
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    return log_file


def main(debug_mode: bool = False):
    """Main function to run the Kindle Reading Assistant"""
    import time
    import traceback
    
    start_time = time.time()
    log_file = setup_logging(debug_mode)
    logger = logging.getLogger(__name__)
    
    logger.info("="*60)
    logger.info("Kindle Reading Assistant Started")
    logger.info(f"Log file: {log_file}")
    logger.info(f"Debug mode: {debug_mode}")
    logger.info("="*60)
    
    try:
        # Initialize components
        logger.info("Initializing components...")
        
        logger.debug("Creating KindleParser...")
        parser = KindleParser()
        logger.debug("KindleParser created successfully")
        
        logger.debug("Creating AIAnalysisInterface (LLM mode)...")
        ai_interface = AIAnalysisInterface(mock_mode=False)  # 使用真实LLM
        logger.debug("AIAnalysisInterface created successfully")
        
        logger.debug("Creating ObsidianGenerator...")
        obsidian_generator = ObsidianGenerator(output_dir="obsidian_vault_llm")
        logger.debug("ObsidianGenerator created successfully")
        
        logger.info("All components initialized successfully")
        
        # Process materials directory
        logger.info("Checking material directory...")
        material_dir = Path("material")
        if not material_dir.exists():
            logger.error(f"Material directory not found: {material_dir}")
            return 1
        
        logger.debug(f"Material directory exists: {material_dir.absolute()}")
        
        # Find all HTML files
        logger.info("Searching for HTML files...")
        html_files = list(material_dir.glob("*.html"))
        if not html_files:
            logger.warning("No HTML files found in material directory")
            return 1
        
        logger.info(f"Found {len(html_files)} HTML files to process:")
        for i, file in enumerate(html_files, 1):
            logger.info(f"  {i}. {file.name} ({file.stat().st_size} bytes)")
        
        # Process each file
        all_results = []
        successful_files = 0
        failed_files = 0
        
        for file_index, html_file in enumerate(html_files, 1):
            try:
                logger.info(f"[{file_index}/{len(html_files)}] Processing {html_file.name}")
                file_start_time = time.time()
                
                # Parse HTML file
                logger.debug(f"Step 1: Parsing HTML file {html_file.name}")
                book = parser.parse_file(str(html_file))
                logger.info(f"Parsed book: '{book.metadata.title}' with {len(book.highlights)} highlights")
                
                # Analyze content with batch processing
                from src.config.settings import Config
                logger.debug(f"Step 2: Starting AI analysis for {len(book.highlights)} highlights (batch_size={Config.AI_BATCH_SIZE})")
                analysis_start_time = time.time()
                analysis_result = ai_interface.analyze_book(book, batch_size=Config.AI_BATCH_SIZE)
                analysis_duration = time.time() - analysis_start_time
                logger.info(f"AI analysis completed in {analysis_duration:.2f}s")
                
                all_results.append(analysis_result)
                
                # Generate Obsidian files with configured mode
                from src.config.settings import Config
                mode_text = "aggregated" if Config.OUTPUT_AGGREGATED_MODE else "individual"
                logger.debug(f"Step 3: Generating Obsidian files ({mode_text} mode)")
                generate_start_time = time.time()
                obsidian_generator.generate_book_files(book, analysis_result, aggregated_mode=Config.OUTPUT_AGGREGATED_MODE)
                generate_duration = time.time() - generate_start_time
                logger.info(f"Obsidian files generated in {generate_duration:.2f}s")
                
                file_duration = time.time() - file_start_time
                successful_files += 1
                logger.info(f"✅ Successfully processed {html_file.name} in {file_duration:.2f}s")
                
            except Exception as e:
                failed_files += 1
                file_duration = time.time() - file_start_time if 'file_start_time' in locals() else 0
                logger.error(f"❌ Error processing {html_file.name} after {file_duration:.2f}s: {e}")
                logger.error(f"Error traceback:\n{traceback.format_exc()}")
                continue
        
        # Generate summary report
        logger.info("Generating summary report...")
        if all_results:
            generate_summary_report(all_results)
            logger.info("Summary report generated successfully")
        else:
            logger.warning("No results to summarize")
        
        # Final statistics
        total_duration = time.time() - start_time
        logger.info("="*60)
        logger.info("Processing Summary:")
        logger.info(f"  • Total files: {len(html_files)}")
        logger.info(f"  • Successful: {successful_files}")
        logger.info(f"  • Failed: {failed_files}")
        logger.info(f"  • Total time: {total_duration:.2f}s")
        logger.info(f"  • Log file: {log_file}")
        logger.info("Kindle Reading Assistant Completed")
        logger.info("="*60)
        
        return 0 if failed_files == 0 else 1
        
    except Exception as e:
        logger.error(f"Fatal error in main function: {e}")
        logger.error(f"Fatal error traceback:\n{traceback.format_exc()}")
        return 1


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
    import sys
    import argparse
    
    # 设置命令行参数
    parser = argparse.ArgumentParser(description="Kindle Reading Assistant - AI-powered book analysis")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode for verbose logging")
    args = parser.parse_args()
    
    # 运行主程序
    exit_code = main(debug_mode=args.debug)
    sys.exit(exit_code)