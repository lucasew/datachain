import sys

def report_error(exception: Exception, context: str = ""):
    """
    Centralized error reporting mechanism.
    Funnel all caught errors through this function.
    """
    if context:
        print(f"Error [{context}]: {exception}", file=sys.stderr)
    else:
        print(f"Error: {exception}", file=sys.stderr)
