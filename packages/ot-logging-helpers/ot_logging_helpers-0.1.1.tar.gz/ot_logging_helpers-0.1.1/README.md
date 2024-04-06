# ot-logging-helpers

This python package provides logging helpers that are used in Orthanc Team projects.

## Demo

```python
from ot_logging_helpers import LogContext, configure_logging
import logging
import threading

configure_logging()

with LogContext("1ST"):
    logging.info("my first message")
    with LogContext("2ND"):
        logging.info("my second message")


def worker(worker_id):
    with LogContext(f"Worker {worker_id}"):
        logging.info("my top level worker message")

        with LogContext("next-context"):
            logging.warning("my warning")

for i in range(0, 2):
    thread = threading.Thread(target=worker, args=(i+1, ))
    thread.start()


###### this shall output 
# 2024-04-05 15:05:28,162 - root       - INFO     -  1ST | my first message
# 2024-04-05 15:05:28,162 - root       - INFO     -  1ST | 2ND | my second message
# 2024-04-05 15:05:28,163 - root       - INFO     -  Worker 1 | my top level worker message
# 2024-04-05 15:05:28,163 - root       - WARNING  -  Worker 1 | next-context | my warning
# 2024-04-05 15:05:28,163 - root       - INFO     -  Worker 2 | my top level worker message
# 2024-04-05 15:05:28,163 - root       - WARNING  -  Worker 2 | next-context | my warning

```
