"""
Logger utility for Master Dashboard Agent
Provides comprehensive logging configuration with file rotation, console output,
and structured logging for better debugging and monitoring
"""
import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import json
import time
from datetime import datetime

try:
    import colorlog
    COLORLOG_AVAILABLE = True
except ImportError:
    COLORLOG_AVAILABLE = False

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)

class AgentLogger:
    """Advanced logger for Master Dashboard Agent"""
    
    def __init__(self, name: str = "master_dashboard_agent"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.handlers = {}
        
    def setup_file_logging(self, 
                          log_file: str = "agent.log",
                          level: str = "INFO",
                          max_size: int = 10,
                          backup_count: int = 5,
                          format_type: str = "standard") -> logging.Handler:
        """Setup file logging with rotation"""
        
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_size * 1024 * 1024,  # Convert MB to bytes
            backupCount=backup_count,
            encoding='utf-8'
        )
        
        # Set level
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        file_handler.setLevel(numeric_level)
        
        # Set formatter
        if format_type == "json":
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
        self.handlers['file'] = file_handler
        
        return file_handler
    
    def setup_console_logging(self, 
                            level: str = "INFO",
                            colored: bool = True) -> logging.Handler:
        """Setup console logging with optional colors"""
        
        console_handler = logging.StreamHandler(sys.stdout)
        
        # Set level
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        console_handler.setLevel(numeric_level)
        
        # Set formatter
        if colored and COLORLOG_AVAILABLE:
            formatter = colorlog.ColoredFormatter(
                '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s',
                datefmt='%H:%M:%S',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                }
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
        
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(console_handler)
        self.handlers['console'] = console_handler
        
        return console_handler
    
    def setup_syslog_logging(self, 
                           address: str = '/dev/log',
                           facility: int = logging.handlers.SysLogHandler.LOG_DAEMON,
                           level: str = "INFO") -> Optional[logging.Handler]:
        """Setup syslog logging (Unix systems only)"""
        try:
            syslog_handler = logging.handlers.SysLogHandler(
                address=address,
                facility=facility
            )
            
            # Set level
            numeric_level = getattr(logging, level.upper(), logging.INFO)
            syslog_handler.setLevel(numeric_level)
            
            # Set formatter
            formatter = logging.Formatter(
                '%(name)s[%(process)d]: %(levelname)s - %(message)s'
            )
            syslog_handler.setFormatter(formatter)
            
            # Add handler to logger
            self.logger.addHandler(syslog_handler)
            self.handlers['syslog'] = syslog_handler
            
            return syslog_handler
            
        except Exception as e:
            print(f"Failed to setup syslog logging: {e}")
            return None
    
    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance"""
        return self.logger
    
    def add_context(self, **kwargs) -> 'ContextLogger':
        """Add context to logger"""
        return ContextLogger(self.logger, kwargs)
    
    def close_handlers(self):
        """Close all handlers"""
        for handler in self.handlers.values():
            handler.close()
            self.logger.removeHandler(handler)
        self.handlers.clear()

class ContextLogger:
    """Logger wrapper that adds context to log messages"""
    
    def __init__(self, logger: logging.Logger, context: Dict[str, Any]):
        self.logger = logger
        self.context = context
    
    def _add_context(self, record):
        """Add context to log record"""
        record.extra_fields = self.context
        return record
    
    def debug(self, msg, *args, **kwargs):
        """Log debug message with context"""
        if self.logger.isEnabledFor(logging.DEBUG):
            record = self.logger.makeRecord(
                self.logger.name, logging.DEBUG, "", 0, msg, args, None
            )
            self._add_context(record)
            self.logger.handle(record)
    
    def info(self, msg, *args, **kwargs):
        """Log info message with context"""
        if self.logger.isEnabledFor(logging.INFO):
            record = self.logger.makeRecord(
                self.logger.name, logging.INFO, "", 0, msg, args, None
            )
            self._add_context(record)
            self.logger.handle(record)
    
    def warning(self, msg, *args, **kwargs):
        """Log warning message with context"""
        if self.logger.isEnabledFor(logging.WARNING):
            record = self.logger.makeRecord(
                self.logger.name, logging.WARNING, "", 0, msg, args, None
            )
            self._add_context(record)
            self.logger.handle(record)
    
    def error(self, msg, *args, **kwargs):
        """Log error message with context"""
        if self.logger.isEnabledFor(logging.ERROR):
            record = self.logger.makeRecord(
                self.logger.name, logging.ERROR, "", 0, msg, args, None
            )
            self._add_context(record)
            self.logger.handle(record)
    
    def critical(self, msg, *args, **kwargs):
        """Log critical message with context"""
        if self.logger.isEnabledFor(logging.CRITICAL):
            record = self.logger.makeRecord(
                self.logger.name, logging.CRITICAL, "", 0, msg, args, None
            )
            self._add_context(record)
            self.logger.handle(record)

def setup_logger(name: str = "master_dashboard_agent",
                level: str = "INFO",
                log_file: Optional[str] = None,
                console: bool = True,
                colored: bool = True,
                json_format: bool = False,
                max_size: int = 10,
                backup_count: int = 5) -> logging.Logger:
    """
    Setup logger with specified configuration
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: File path for file logging (None to disable)
        console: Enable console logging
        colored: Enable colored console output
        json_format: Use JSON format for file logging
        max_size: Maximum log file size in MB
        backup_count: Number of backup files to keep
    
    Returns:
        Configured logger instance
    """
    agent_logger = AgentLogger(name)
    
    # Setup file logging if requested
    if log_file:
        format_type = "json" if json_format else "standard"
        agent_logger.setup_file_logging(
            log_file=log_file,
            level=level,
            max_size=max_size,
            backup_count=backup_count,
            format_type=format_type
        )
    
    # Setup console logging if requested
    if console:
        agent_logger.setup_console_logging(
            level=level,
            colored=colored
        )
    
    # Setup syslog on Unix systems
    try:
        import platform
        if platform.system().lower() != 'windows':
            agent_logger.setup_syslog_logging(level=level)
    except:
        pass
    
    return agent_logger.get_logger()

# Performance logging decorator
def log_performance(logger: logging.Logger, level: int = logging.DEBUG):
    """Decorator to log function performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.log(level, f"{func.__name__} executed in {execution_time:.4f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"{func.__name__} failed after {execution_time:.4f}s: {e}")
                raise
        return wrapper
    return decorator