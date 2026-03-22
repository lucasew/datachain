import sys

def report_error(error, context=None):
    """
    Centralized error reporting function.
    Funneled through this function instead of scattered empty catch blocks
    or direct prints to stderr.
    """
    if context:
        print(f"Error [{context}]: {type(error).__name__} - {error}", file=sys.stderr)
    else:
        print(f"Error: {type(error).__name__} - {error}", file=sys.stderr)
    # If Sentry were configured, we would call Sentry.captureException(error) here.
