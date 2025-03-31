import logging
import os
import sys
import time
from enum import Enum
from typing import Optional, Dict, Any, Union, List, Set
import inspect

# ANSI color codes for terminal output


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class LogLevel(Enum):
    """Log levels with integer values compatible with Python's logging module"""
    DEBUG = logging.DEBUG      # 10 - Detailed information, typically of interest only when diagnosing problems
    INFO = logging.INFO        # 20 - Confirmation that things are working as expected
    # 30 - An indication that something unexpected happened, or may happen
    WARNING = logging.WARNING
    # 40 - Due to a more serious problem, the software has not been able to perform a function
    ERROR = logging.ERROR
    # 50 - A serious error, indicating that the program itself may be unable to continue
    CRITICAL = logging.CRITICAL


class ModuleFilter(logging.Filter):
    """Filter that excludes logs from specified modules/packages"""

    def __init__(self, excluded_modules: List[str]):
        super().__init__()
        self.excluded_modules = excluded_modules

    def filter(self, record):
        # Allow the record through if its module is not in the excluded list
        for module in self.excluded_modules:
            if record.name.startswith(module):
                return False
        return True


class AgentLogger:
    """
    Custom logger for the LangGraph agent system with colored output and different debug levels.

    This logger makes it easy to trace the flow of execution through the agent pipeline,
    with configurable verbosity and colorful formatting for better readability.
    """

    _instance = None
    _loggers: Dict[str, logging.Logger] = {}
    _global_level = LogLevel.INFO
    _initialized = False
    _filtered_modules = ["openai", "httpx", "httpcore"]
    _show_filtered = False

    def __new__(cls, *args, **kwargs):
        """Implement singleton pattern to ensure consistent logging configuration"""
        if cls._instance is None:
            cls._instance = super(AgentLogger, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Set up the base logger configuration"""
        if self._initialized:
            return

        # Configure the root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(self._global_level.value)

        # Remove existing handlers to avoid duplicate logs
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self._global_level.value)

        # Apply module filtering
        if not self._show_filtered:
            console_handler.addFilter(ModuleFilter(self._filtered_modules))

        # Create formatter with colors
        formatter = logging.Formatter(
            f'{Colors.BOLD}%(asctime)s{Colors.END} | '
            f'%(levelname)-8s | '
            f'%(name)s | '
            f'%(message)s'
        )
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # Set third-party loggers to WARNING by default
        for module in self._filtered_modules:
            logging.getLogger(module).setLevel(logging.WARNING)

        # Force propagation to root logger
        logging.getLogger('src').propagate = True

        # Mark as initialized
        self._initialized = True

        # Print a test message to verify logging is working
        test_logger = logging.getLogger("AgentLogger")
        test_logger.info(
            f"{Colors.GREEN}Logging system initialized{Colors.END}")
        if not self._show_filtered:
            test_logger.info(
                f"{Colors.BLUE}OpenAI and HTTP logs are filtered. Use show_filtered(True) to show them.{Colors.END}")

    @classmethod
    def get_logger(cls, name: Optional[str] = None) -> logging.Logger:
        """
        Get a logger instance with the specified name.

        Args:
            name: Logger name, typically the module name. If None, auto-detects the caller module.

        Returns:
            Configured Logger instance
        """
        # Ensure initialized
        if not cls._initialized:
            cls._instance = cls()

        # Auto-detect caller module if name not provided
        if name is None:
            # Get the calling frame
            frame = inspect.currentframe().f_back
            module = inspect.getmodule(frame)
            name = module.__name__ if module else "unknown"

        # Create logger if it doesn't exist
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            # Ensure logger has correct level
            logger.setLevel(cls._global_level.value)
            cls._loggers[name] = logger

        return cls._loggers[name]

    @classmethod
    def set_level(cls, level: Union[LogLevel, int, str]):
        """
        Set the global logging level.

        Args:
            level: Logging level as LogLevel enum, integer, or string
        """
        # Convert string to enum if needed
        if isinstance(level, str):
            level = LogLevel[level.upper()]

        # Convert integer to enum if needed
        if isinstance(level, int):
            for log_level in LogLevel:
                if log_level.value == level:
                    level = log_level
                    break

        # Update global level
        cls._global_level = level

        # Update root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(level.value)

        # Update all handlers
        for handler in root_logger.handlers:
            handler.setLevel(level.value)

        # Update all existing loggers
        for logger_name, logger in cls._loggers.items():
            logger.setLevel(level.value)

        # Log the level change
        print(
            f"{Colors.BOLD}[INFO]{Colors.END} | AgentLogger | Log level set to {level.name}")
        cls.get_logger("AgentLogger").info(f"Log level set to {level.name}")

    @classmethod
    def show_filtered(cls, show: bool = True):
        """
        Control whether to show logs from filtered modules (OpenAI, HTTP libraries).

        Args:
            show: True to show all logs, False to filter third-party logs
        """
        cls._show_filtered = show

        # Re-initialize to apply the changes
        root_logger = logging.getLogger()

        # Update all handlers' filters
        for handler in root_logger.handlers:
            # Remove existing module filters
            for filter in handler.filters[:]:
                if isinstance(filter, ModuleFilter):
                    handler.removeFilter(filter)

            # Add new filter if needed
            if not show:
                handler.addFilter(ModuleFilter(cls._filtered_modules))

        # Update log levels for third-party modules
        for module in cls._filtered_modules:
            level = cls._global_level.value if show else logging.WARNING
            logging.getLogger(module).setLevel(level)

        # Log the change
        msg = "Showing" if show else "Hiding"
        cls.get_logger("AgentLogger").info(
            f"{msg} logs from {', '.join(cls._filtered_modules)}")

    @staticmethod
    def debug(msg: str, *args, **kwargs):
        """Log a debug message from the calling module"""
        frame = inspect.currentframe().f_back
        module = inspect.getmodule(frame)
        name = module.__name__ if module else "unknown"
        logger = AgentLogger.get_logger(name)
        logger.debug(f"{Colors.BLUE}{msg}{Colors.END}", *args, **kwargs)

    @staticmethod
    def info(msg: str, *args, **kwargs):
        """Log an info message from the calling module"""
        frame = inspect.currentframe().f_back
        module = inspect.getmodule(frame)
        name = module.__name__ if module else "unknown"
        logger = AgentLogger.get_logger(name)
        logger.info(f"{Colors.GREEN}{msg}{Colors.END}", *args, **kwargs)

    @staticmethod
    def warning(msg: str, *args, **kwargs):
        """Log a warning message from the calling module"""
        frame = inspect.currentframe().f_back
        module = inspect.getmodule(frame)
        name = module.__name__ if module else "unknown"
        logger = AgentLogger.get_logger(name)
        logger.warning(f"{Colors.YELLOW}{msg}{Colors.END}", *args, **kwargs)

    @staticmethod
    def error(msg: str, *args, **kwargs):
        """Log an error message from the calling module"""
        frame = inspect.currentframe().f_back
        module = inspect.getmodule(frame)
        name = module.__name__ if module else "unknown"
        logger = AgentLogger.get_logger(name)
        logger.error(f"{Colors.RED}{msg}{Colors.END}", *args, **kwargs)

    @staticmethod
    def critical(msg: str, *args, **kwargs):
        """Log a critical message from the calling module"""
        frame = inspect.currentframe().f_back
        module = inspect.getmodule(frame)
        name = module.__name__ if module else "unknown"
        logger = AgentLogger.get_logger(name)
        logger.critical(
            f"{Colors.RED}{Colors.BOLD}{msg}{Colors.END}", *args, **kwargs)

    @staticmethod
    def log_state(state: Dict[str, Any], label: str = "AGENT STATE"):
        """
        Log the current state of the agent for debugging purposes.

        Args:
            state: The agent state dictionary to log
            label: Optional label for the state log entry
        """
        frame = inspect.currentframe().f_back
        module = inspect.getmodule(frame)
        name = module.__name__ if module else "unknown"
        logger = AgentLogger.get_logger(name)

        if logger.level <= LogLevel.DEBUG.value:
            # Only log detailed state at DEBUG level
            logger.debug(f"{Colors.CYAN}==== {label} ===={Colors.END}")

            if "messages" in state and state["messages"]:
                logger.debug(
                    f"{Colors.CYAN}Messages (count: {len(state['messages'])}):{Colors.END}")
                for i, msg in enumerate(state["messages"]):
                    content = msg.content if hasattr(
                        msg, 'content') else str(msg)
                    sender = msg.name if hasattr(msg, 'name') else "System"
                    # Truncate long messages
                    if len(content) > 100:
                        content = content[:97] + "..."
                    logger.debug(
                        f"{Colors.CYAN}  [{i}] {sender}: {content}{Colors.END}")

            # Log profile and scenario keys without full content (which would be too verbose)
            for key in ["studentProfile", "scenario"]:
                if key in state and state[key]:
                    logger.debug(
                        f"{Colors.CYAN}{key}: [Present - {len(str(state[key]))} chars]{Colors.END}")

            # Log other keys
            for key, value in state.items():
                if key not in ["messages", "studentProfile", "scenario"]:
                    logger.debug(f"{Colors.CYAN}{key}: {value}{Colors.END}")

            logger.debug(
                f"{Colors.CYAN}===={'=' * len(label)}===={Colors.END}")


# Create a package __init__.py
__all__ = ['AgentLogger', 'LogLevel']
