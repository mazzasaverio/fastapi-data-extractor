import sys
from typing import Optional
from loguru import logger


class LoggingManager:
    """
    Centralized logging manager using Loguru
    Provides structured logging with consistent formatting
    """
    
    _configured = False
    
    @classmethod
    def configure_logging(cls, level: str = "INFO", debug: bool = False) -> None:
        """Configure loguru logger with appropriate settings"""
        if cls._configured:
            return
            
        # Remove default handler
        logger.remove()
        
        # Configure log level based on debug mode
        log_level = "DEBUG" if debug else level
        
        # Add console handler with structured format
        logger.add(
            sys.stdout,
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
            colorize=True,
            diagnose=debug
        )
        
        # Add file handler for errors
        logger.add(
            "logs/error.log",
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation="10 MB",
            retention="30 days",
            compression="zip"
        )
        
        # Add file handler for all logs if debug
        if debug:
            logger.add(
                "logs/debug.log",
                level="DEBUG",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
                rotation="50 MB",
                retention="7 days",
                compression="zip"
            )
        
        cls._configured = True
        logger.info("Logging configured successfully")
    
    @classmethod
    def get_logger(cls, name: Optional[str] = None):
        """Get a logger instance with optional name binding"""
        if not cls._configured:
            cls.configure_logging()
        
        if name:
            return logger.bind(name=name)
        return logger
    
    @classmethod
    def add_file_handler(cls, file_path: str, level: str = "INFO", 
                        rotation: str = "10 MB", retention: str = "30 days") -> None:
        """Add additional file handler"""
        logger.add(
            file_path,
            level=level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation=rotation,
            retention=retention,
            compression="zip"
        )
        logger.info(f"Added file handler: {file_path}")
    
    @classmethod
    def set_level(cls, level: str) -> None:
        """Change logging level dynamically"""
        # This would require more complex implementation to change existing handlers
        logger.info(f"Logging level change requested: {level}") 