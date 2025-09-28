"""
Centralized configuration management system.

This module provides a unified configuration system that eliminates scattered
configuration handling across the codebase and provides validation, defaults,
and environment-based configuration loading.
"""
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv

from ..utils.exceptions import InvalidConfigurationError
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class DatabaseConfig:
    """Database connection configuration."""
    host: str = "localhost"
    port: int = 5432
    name: str = "college_db"
    user: str = "postgres"
    password: str = ""
    pool_min_size: int = 5
    pool_max_size: int = 20
    command_timeout: int = 60
    connection_timeout: int = 10

    def get_connection_string(self) -> str:
        """Get PostgreSQL connection string."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    def validate(self) -> None:
        """Validate database configuration."""
        if not self.host:
            raise InvalidConfigurationError("Database host is required")
        if not self.name:
            raise InvalidConfigurationError("Database name is required")
        if not self.user:
            raise InvalidConfigurationError("Database user is required")
        if self.port <= 0 or self.port > 65535:
            raise InvalidConfigurationError("Database port must be between 1 and 65535")
        if self.pool_min_size < 1:
            raise InvalidConfigurationError("Database pool minimum size must be at least 1")
        if self.pool_max_size < self.pool_min_size:
            raise InvalidConfigurationError("Database pool maximum size must be >= minimum size")


@dataclass
class AIServiceConfig:
    """AI service configuration."""
    google_api_key: str = ""
    gptzero_api_key: str = ""
    model: str = "gemini-2.5-flash"
    temperature: float = 0.3
    max_tokens: Optional[int] = None
    timeout: int = 120
    retry_attempts: int = 3
    retry_delay: float = 1.0

    def validate(self) -> None:
        """Validate AI service configuration."""
        if not self.google_api_key:
            raise InvalidConfigurationError("Google AI API key is required")
        if self.temperature < 0.0 or self.temperature > 2.0:
            raise InvalidConfigurationError("Temperature must be between 0.0 and 2.0")
        if self.max_tokens is not None and self.max_tokens <= 0:
            raise InvalidConfigurationError("Max tokens must be positive")
        if self.timeout <= 0:
            raise InvalidConfigurationError("Timeout must be positive")
        if self.retry_attempts < 0:
            raise InvalidConfigurationError("Retry attempts cannot be negative")


@dataclass
class ProcessingConfig:
    """Content processing configuration."""
    default_delay: float = 1.0
    max_retries: int = 3
    ai_score_threshold: float = 90.0
    batch_size: int = 10
    enable_ai_validation: bool = True
    enable_humanization: bool = True
    save_to_database: bool = True

    def validate(self) -> None:
        """Validate processing configuration."""
        if self.default_delay < 0:
            raise InvalidConfigurationError("Default delay cannot be negative")
        if self.max_retries < 1:
            raise InvalidConfigurationError("Max retries must be at least 1")
        if self.ai_score_threshold < 0 or self.ai_score_threshold > 100:
            raise InvalidConfigurationError("AI score threshold must be between 0 and 100")
        if self.batch_size < 1:
            raise InvalidConfigurationError("Batch size must be at least 1")


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_file_logging: bool = False
    log_file_path: str = "logs/app.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

    def validate(self) -> None:
        """Validate logging configuration."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.level.upper() not in valid_levels:
            raise InvalidConfigurationError(f"Log level must be one of: {valid_levels}")
        if self.max_file_size <= 0:
            raise InvalidConfigurationError("Max file size must be positive")
        if self.backup_count < 0:
            raise InvalidConfigurationError("Backup count cannot be negative")


@dataclass
class ContentTypeConfig:
    """Configuration for specific content types."""
    overview: Dict[str, str] = field(default_factory=lambda: {
        "tab_name": "overview",
        "short_tab_name": "overview",
        "generator_class": "CollegeOverviewGenerator",
        "short_generator_class": "CollegeOverviewShortGenerator"
    })
    courses: Dict[str, str] = field(default_factory=lambda: {
        "tab_name": "all_courses",
        "short_tab_name": "all_courses",
        "generator_class": "CourseContentGenerator",
        "short_generator_class": "CourseShortContentGenerator"
    })
    fees: Dict[str, str] = field(default_factory=lambda: {
        "tab_name": "fees",
        "generator_class": "FeesContentGenerator"
    })
    reviews: Dict[str, str] = field(default_factory=lambda: {
        "tab_name": "reviews",
        "generator_class": "ReviewsContentGenerator"
    })
    campus: Dict[str, str] = field(default_factory=lambda: {
        "tab_name": "campus",
        "generator_class": "CampusContentGenerator"
    })


@dataclass
class ApplicationConfig:
    """Main application configuration."""
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    ai_services: AIServiceConfig = field(default_factory=AIServiceConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    content_types: ContentTypeConfig = field(default_factory=ContentTypeConfig)

    # Application metadata
    app_name: str = "AI SEO Optimizer"
    version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False

    def validate(self) -> None:
        """Validate all configuration sections."""
        try:
            self.database.validate()
            self.ai_services.validate()
            self.processing.validate()
            self.logging.validate()
            logger.info("Configuration validation successful")
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise InvalidConfigurationError(f"Configuration validation failed: {e}")

    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> 'ApplicationConfig':
        """
        Load configuration from environment variables.

        Args:
            env_file: Path to .env file (optional)

        Returns:
            ApplicationConfig instance loaded from environment
        """
        # Load environment variables
        if env_file:
            load_dotenv(env_file)
        else:
            # Try to find .env file in common locations
            for env_path in ['.env', '../.env', '../../.env']:
                if Path(env_path).exists():
                    load_dotenv(env_path)
                    break

        # Database configuration
        database = DatabaseConfig(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            name=os.getenv('DB_NAME', 'college_db'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', ''),
            pool_min_size=int(os.getenv('DB_POOL_MIN_SIZE', '5')),
            pool_max_size=int(os.getenv('DB_POOL_MAX_SIZE', '20')),
            command_timeout=int(os.getenv('DB_COMMAND_TIMEOUT', '60')),
            connection_timeout=int(os.getenv('DB_CONNECTION_TIMEOUT', '10'))
        )

        # AI services configuration
        ai_services = AIServiceConfig(
            google_api_key=os.getenv('GOOGLE_API_KEY', ''),
            gptzero_api_key=os.getenv('GPTZERO_API_KEY', ''),
            model=os.getenv('AI_MODEL', 'gemini-2.5-flash'),
            temperature=float(os.getenv('AI_TEMPERATURE', '0.3')),
            max_tokens=int(os.getenv('AI_MAX_TOKENS')) if os.getenv('AI_MAX_TOKENS') else None,
            timeout=int(os.getenv('AI_TIMEOUT', '120')),
            retry_attempts=int(os.getenv('AI_RETRY_ATTEMPTS', '3')),
            retry_delay=float(os.getenv('AI_RETRY_DELAY', '1.0'))
        )

        # Processing configuration
        processing = ProcessingConfig(
            default_delay=float(os.getenv('PROCESSING_DEFAULT_DELAY', '1.0')),
            max_retries=int(os.getenv('PROCESSING_MAX_RETRIES', '3')),
            ai_score_threshold=float(os.getenv('PROCESSING_AI_THRESHOLD', '90.0')),
            batch_size=int(os.getenv('PROCESSING_BATCH_SIZE', '10')),
            enable_ai_validation=os.getenv('PROCESSING_ENABLE_AI_VALIDATION', 'true').lower() == 'true',
            enable_humanization=os.getenv('PROCESSING_ENABLE_HUMANIZATION', 'true').lower() == 'true',
            save_to_database=os.getenv('PROCESSING_SAVE_TO_DB', 'true').lower() == 'true'
        )

        # Logging configuration
        logging_config = LoggingConfig(
            level=os.getenv('LOG_LEVEL', 'INFO').upper(),
            format=os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            enable_file_logging=os.getenv('LOG_ENABLE_FILE', 'false').lower() == 'true',
            log_file_path=os.getenv('LOG_FILE_PATH', 'logs/app.log'),
            max_file_size=int(os.getenv('LOG_MAX_FILE_SIZE', str(10 * 1024 * 1024))),
            backup_count=int(os.getenv('LOG_BACKUP_COUNT', '5'))
        )

        # Application metadata
        app_name = os.getenv('APP_NAME', 'AI SEO Optimizer')
        version = os.getenv('APP_VERSION', '1.0.0')
        environment = os.getenv('ENVIRONMENT', 'development')
        debug = os.getenv('DEBUG', 'false').lower() == 'true'

        config = cls(
            database=database,
            ai_services=ai_services,
            processing=processing,
            logging=logging_config,
            app_name=app_name,
            version=version,
            environment=environment,
            debug=debug
        )

        # Validate configuration
        config.validate()

        logger.info(f"Loaded configuration for {config.app_name} v{config.version} ({config.environment})")
        return config

    def to_dict(self) -> Dict:
        """Convert configuration to dictionary (excluding sensitive data)."""
        config_dict = {
            'app_name': self.app_name,
            'version': self.version,
            'environment': self.environment,
            'debug': self.debug,
            'database': {
                'host': self.database.host,
                'port': self.database.port,
                'name': self.database.name,
                'user': self.database.user,
                'pool_min_size': self.database.pool_min_size,
                'pool_max_size': self.database.pool_max_size,
                # password excluded for security
            },
            'ai_services': {
                'model': self.ai_services.model,
                'temperature': self.ai_services.temperature,
                'max_tokens': self.ai_services.max_tokens,
                'timeout': self.ai_services.timeout,
                'retry_attempts': self.ai_services.retry_attempts,
                # API keys excluded for security
            },
            'processing': {
                'default_delay': self.processing.default_delay,
                'max_retries': self.processing.max_retries,
                'ai_score_threshold': self.processing.ai_score_threshold,
                'batch_size': self.processing.batch_size,
                'enable_ai_validation': self.processing.enable_ai_validation,
                'enable_humanization': self.processing.enable_humanization,
                'save_to_database': self.processing.save_to_database,
            },
            'logging': {
                'level': self.logging.level,
                'enable_file_logging': self.logging.enable_file_logging,
                'log_file_path': self.logging.log_file_path,
            }
        }
        return config_dict


# Global configuration instance
_global_config: Optional[ApplicationConfig] = None


def get_config(env_file: Optional[str] = None) -> ApplicationConfig:
    """
    Get or create the global configuration instance.

    Args:
        env_file: Path to .env file (optional)

    Returns:
        ApplicationConfig instance
    """
    global _global_config

    if _global_config is None:
        _global_config = ApplicationConfig.from_env(env_file)

    return _global_config


def reload_config(env_file: Optional[str] = None) -> ApplicationConfig:
    """
    Reload the global configuration from environment.

    Args:
        env_file: Path to .env file (optional)

    Returns:
        Reloaded ApplicationConfig instance
    """
    global _global_config
    _global_config = ApplicationConfig.from_env(env_file)
    return _global_config


# Convenience functions for accessing specific configuration sections
def get_database_config() -> DatabaseConfig:
    """Get database configuration."""
    return get_config().database


def get_ai_services_config() -> AIServiceConfig:
    """Get AI services configuration."""
    return get_config().ai_services


def get_processing_config() -> ProcessingConfig:
    """Get processing configuration."""
    return get_config().processing


def get_logging_config() -> LoggingConfig:
    """Get logging configuration."""
    return get_config().logging