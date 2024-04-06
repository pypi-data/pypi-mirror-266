import logging
from .log_context import get_log_context


class CustomFormatter(logging.Formatter):
    def format(self, record):
        context = get_log_context()
        if len(context) > 0:
            context_str = ' ' + ' | '.join(context) + ' | '
            # Add the context information to the log message
            record.msg = f"{context_str}{record.msg}"

        record.name = record.name[:10].ljust(10)
        record.levelname = record.levelname[:8].ljust(8)

        return super().format(record)