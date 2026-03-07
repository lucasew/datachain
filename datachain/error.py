import sys


def report_error(msg, error=None, **context):
    """
    Centralized error reporting function.
    Currently logs to sys.stderr, but designed to be Sentry-aware or extensible later.
    """
    out = [str(msg)]
    if error is not None:
        out.append(f"Error: {repr(error)}")
    if context:
        out.append(f"Context: {context}")
    print(" | ".join(out), file=sys.stderr)
