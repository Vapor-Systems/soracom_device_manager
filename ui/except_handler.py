"""
Exception handler for the Soracom Device Manager.
Provides custom exception handling to prevent premature exit.
"""

class UpdateExitException(Exception):
    """Custom exception for graceful termination of update process"""
    pass

def handle_update_exception(func):
    """
    Decorator to handle exceptions during the update process
    without triggering program exit.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Print the exception but don't exit
            from core import print_status
            print_status(f"Error caught in update process: {str(e)}", "error")
            # Return False to indicate failure
            return False
    return wrapper
