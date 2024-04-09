class UnsupportedLLMProvider(Exception):
    """The exception class for unsupported LLM provider"""


class InvalidApiKey(Exception):
    """The exception class for InvalidApiKey"""


class MissingApiKey(Exception):
    """The exception class for MissingApiKey"""


class MissingLLMProviders(Exception):
    """The exception class for empty LLM providers array"""


class ApiError(Exception):
    """The exception class for any ApiError"""
