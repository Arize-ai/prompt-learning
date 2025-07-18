from typing import Optional


class KeywordException:
    """Base class for all keyword exceptions"""

    KEYWORD: str = "error"
    message: Optional[str] = None
    details: Optional[str] = None


class RateLimitException(KeywordException):
    """Exception for rate limit errors"""

    KEYWORD: str = "TOO_MANY_REQUESTS"
    message: str = "Rate limit exceeded"
    details: str = "try adding 'sleep_time' between requests"


class RetryException(KeywordException):
    """Exception for retry errors"""

    KEYWORD: str = "Max retries exceeded"
    message: str = "Maximum retries exceeded - network instability"
    details: str = "wait a few seconds and try again"


class ArizeAPIException(Exception):
    """Base class for all API exceptions"""

    keyword_exceptions = [RateLimitException, RetryException]
    message: str = "An error occurred while running the query"
    details: Optional[str] = None

    def __init__(self, details: Optional[str] = None):
        self.details = details
        for exception in self.keyword_exceptions:
            if exception.KEYWORD in details:
                self.message = exception.message or self.message
                self.details = exception.details or details
        super().__init__(self.message, self.details)

    def __str__(self):
        return f"{self.message} - {self.details}"

    def __repr__(self):
        return self.__str__()
