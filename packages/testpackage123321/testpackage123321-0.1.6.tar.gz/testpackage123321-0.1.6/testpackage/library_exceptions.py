# Import necessary libraries (replace with your actual imports)  # Assuming you're using unstructured.io
import openai  # Assuming you're using OpenAI

class LibraryError(Exception):
    """Base class for all exceptions related to your library."""
    pass

class UnsupportedPythonVersion(LibraryError):
    """Raised when the installed Python version is not supported."""
    def __init__(self):
        super().__init__(
            "This library requires Python 3.9 to 3.11. Please upgrade or downgrade your Python installation."
        )

class DocumentExtractorError(LibraryError):
    """Raised when errors occur during document extraction."""
    pass

class UnstructuredIOError(DocumentExtractorError):
    """Raised when errors occur with the unstructured.io library."""
    def __init__(self, underlying_error=None):
        super().__init__(
            "Error using unstructured.io. "
            f"Specific details (if available): {underlying_error}"
        )

class InvalidFilePath(DocumentExtractorError):
    """Raised when the provided file path is invalid."""
    def __init__(self):
        super().__init__("Invalid file path provided. Please check the path and try again.")

class OpenAIError(LibraryError):
    """Raised when errors occur with the OpenAI API."""
    pass

class InvalidAPIKey(OpenAIError):
    """Raised when the provided OpenAI API key is invalid."""
    def __init__(self):
        super().__init__("Invalid OpenAI API key. Please check your credentials and try again.")

class InvalidToken(OpenAIError):
    """Raised when the provided OpenAI token is invalid."""
    def __init__(self):
        super().__init__("Invalid OpenAI token. Please check your credentials and try again.")

class MaxTokensExceeded(OpenAIError):
    """Raised when the requested number of tokens exceeds OpenAI's limit."""
    def __init__(self):
        super().__init__("Maximum allowed tokens exceeded. Please adjust your request or consider upgrading your OpenAI plan.")

class ChunkingError(LibraryError):
    """Raised when errors occur during text chunking."""
    pass

class TextTooShort(ChunkingError):
    """Raised when the extracted text is too short for the requested chunk size."""
    def __init__(self):
        super().__init__("Extracted text is too short for chunking. Please consider a smaller chunk size.")

class InvalidChunkSize(ChunkingError):
    """Raised when the provided chunk size is invalid."""
    def __init__(self):
        super().__init__("Invalid chunk size provided. Chunk size must be a positive integer.")


