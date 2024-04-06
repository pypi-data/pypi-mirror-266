import logging
from .log_context import get_log_context


class CustomFormatter(logging.Formatter):
    def format(self, record):
        context = get_log_context()
        if len(context) > 0:
            context_str = ' ' + ' | '.join(context) + ' | '
            # Add the context information to the log message
            record.msg = f"{context_str}{record.msg}"

        logger_names_max_length = max(len('root'), max([len(logger.name) for logger in logging.Logger.manager.loggerDict.values() if isinstance(logger, logging.Logger)]))

        record.name = record.name[:logger_names_max_length].ljust(logger_names_max_length)
        record.levelname = record.levelname[:8].ljust(8)

        return super().format(record)