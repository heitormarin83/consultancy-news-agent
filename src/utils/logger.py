"""
Unified logging system for Consultancy News Agent
Using loguru for better logging experience
"""

import os
import sys
from pathlib import Path
from loguru import logger

def setup_logger():
    """Setup loguru logger with appropriate configuration"""
    
    # Remove default handler
    logger.remove()
    
    # Get log level from environment
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Create logs directory
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    # Console handler with colors
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # File handler for all logs
    logger.add(
        logs_dir / "consultancy_agent.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    # Separate file for errors
    logger.add(
        logs_dir / "errors.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="5 MB",
        retention="60 days",
        compression="zip"
    )
    
    # Debug mode
    if os.getenv('DEBUG_MODE', 'false').lower() == 'true':
        logger.add(
            logs_dir / "debug.log",
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="50 MB",
            retention="7 days"
        )

def get_logger(name: str):
    """Get a logger instance with the specified name"""
    return logger.bind(name=name)

# Initialize logging when module is imported
setup_logger()

