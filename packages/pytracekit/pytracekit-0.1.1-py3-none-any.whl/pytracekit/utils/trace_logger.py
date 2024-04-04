import logging
from logging.handlers import RotatingFileHandler
from logging import StreamHandler
from opentelemetry import trace
from opentelemetry.trace import get_current_span


class TraceIdFormatter(logging.Formatter):
    def format(self, record):
        current_span = get_current_span()
        trace_id = trace.format_trace_id(current_span.get_span_context().trace_id) if current_span else 'no-trace'
        record.trace_id = trace_id
        return super().format(record)

def get_logger(name='default_logger', log_file_path=None, max_bytes=10*1024*1024, backup_count=5):
    """
    Configures a logger with optional file logging and rotation.

    Args:
        name (str): The name of the logger. Defaults to 'default_logger'.
        log_file_path (str, optional): Path to the log file. If None, logs to stdout.
        max_bytes (int): Max file size for rotation. Defaults to 10 MB.
        backup_count (int): Number of backup files to keep. Defaults to 5.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if log_file_path:
        handler = RotatingFileHandler(log_file_path, maxBytes=max_bytes, backupCount=backup_count)
    else:
        handler = StreamHandler()  # Defaults to stdout

    formatter = TraceIdFormatter('%(asctime)s %(levelname)s TraceId:[%(trace_id)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter) # setting the log format 
    logger.addHandler(handler)  # specifying the destination of the logs 

    return logger
