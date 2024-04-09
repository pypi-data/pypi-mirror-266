class DangerZone(Exception):
    def __init__(self,message) -> None:
        """Raised when the source path or destination path is OS directory."""
        
        super().__init__(f"Error: {message}.")
        

class DestinationInsideSourceError(Exception):
    """Raised when the destination path is inside the source path."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
