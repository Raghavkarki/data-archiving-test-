"""Application logging utility"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from flask import current_app


def setup_logging(app):
    """Setup application logging"""
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(app.config['BASE_DIR'], 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Log file path
    log_file = os.path.join(logs_dir, 'app.log')
    
    # Set logging level from environment or default to INFO
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    # Configure logging format
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler with rotation (max 10MB, keep 5 backup files)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, log_level))
    file_handler.setFormatter(log_format)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    
    # Configure root logger
    app.logger.setLevel(getattr(logging, log_level))
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    
    # Prevent duplicate logs
    app.logger.propagate = False
    
    app.logger.info(f"Logging initialized. Log file: {log_file}")
    
    return app.logger


def get_logger(name=None):
    """Get a logger instance"""
    if name:
        return logging.getLogger(name)
    return logging.getLogger('app')


def log_request_info():
    """Log request information"""
    from flask import request
    logger = get_logger()
    logger.info(f"Request: {request.method} {request.path} - IP: {request.remote_addr}")


def log_error(error, context=None):
    """Log error with context"""
    logger = get_logger()
    error_msg = f"Error: {str(error)}"
    if context:
        error_msg += f" | Context: {context}"
    logger.error(error_msg, exc_info=True)



