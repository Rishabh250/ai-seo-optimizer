"""
Custom exceptions for the AI SEO Optimizer application.
"""


class AISeOOptimizerError(Exception):
    """Base exception for AI SEO Optimizer application."""
    pass


class DatabaseConnectionError(AISeOOptimizerError):
    """Raised when database connection fails."""
    pass


class CollegeNotFoundError(AISeOOptimizerError):
    """Raised when a college is not found."""
    
    def __init__(self, college_identifier: str, search_type: str = "ID"):
        self.college_identifier = college_identifier
        self.search_type = search_type
        super().__init__(f"College not found with {search_type}: {college_identifier}")


class ContentGenerationError(AISeOOptimizerError):
    """Raised when content generation fails."""
    pass


class InvalidConfigurationError(AISeOOptimizerError):
    """Raised when configuration is invalid."""
    pass


class PromptTemplateError(AISeOOptimizerError):
    """Raised when prompt template processing fails."""
    pass

class ReviewsNotFoundError(AISeOOptimizerError):
    """Raised when reviews are not found."""
    pass