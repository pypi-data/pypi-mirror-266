import threading
import uuid
from typing import List, Optional

local_storage = threading.local() # each thread will have its own private copy!

def push_log_context(contextString: str):
    if not hasattr(local_storage, 'log_context'):
        local_storage.log_context = []
    local_storage.log_context.append(contextString)

def get_log_context() -> List[str]:
    if not hasattr(local_storage, 'log_context'):
        return []
    return local_storage.log_context

def pop_log_context():
    if not hasattr(local_storage, 'log_context'):
        return
    local_storage.log_context.pop()



class LogContext:

    def __init__(self, context_string: Optional[str] = None) -> None:
        # by default, if no context is provided, generate a random string
        if context_string is None:
            self._context_string =  uuid.uuid4().hex.upper()[:8]
        else:
            self._context_string = context_string

    def __enter__(self):
        push_log_context(self._context_string)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pop_log_context()