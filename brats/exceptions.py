class CPUNotCompatibleException(Exception):
    """Exception raised when an CPU-incompatible algorithm tries to run on CPU."""

    def __init__(self, message: str):
        super().__init__(message)
