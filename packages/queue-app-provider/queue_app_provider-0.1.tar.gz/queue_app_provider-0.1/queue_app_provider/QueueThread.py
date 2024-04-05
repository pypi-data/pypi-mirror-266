import logging
import queue
import threading


# This is an independent queue processor thread, it just makes non blocking read
# on a queue and, process results using the handler input method.
# Queue is stopped using provided event_handler
#
# Created by: David Rodríguez Alfayate
# Version: 1.0
from typing import Callable

from queue_app_provider.HandlerOutput import HandlerOutput


class QueueThread(threading.Thread):
    def __init__(self, handler: Callable[[str], HandlerOutput], shared_queue: queue.Queue,
                 event_handler: threading.Event, timeout=30):
        threading.Thread.__init__(self)
        self.handler = handler
        self.queue = shared_queue
        self.event_handler = event_handler
        self.timeout = timeout

    def run(self):
        logging.debug("Starting main queue processor")
        while True:
            # Very simple logic, we are just reading the queue in a non-blocking way,
            # therefore if queue is not empty we recover last entry and process it
            # in any other case we wait (sleep) for a 'timeout' number of seconds.
            #
            # Since we need to stop thread, we are also listening on event_handler,
            # if it's set, processing is stopped and this thread "dies" gracefully
            global_break = False
            while not self.queue.empty():
                if self.event_handler.is_set():
                    global_break = True
                    break
                entry = self.queue.get_nowait()
                entry.handle(self.handler)

            if global_break:
                logging.debug("Breaking thread due to user interrupt")
                break

            # As stated above we wait til handler is set or timeout is exceded,
            # if timeout is exceded we continue with normal workflow, that is
            # run forever ;)
            if self.event_handler.wait(timeout=self.timeout):
                logging.debug("Breaking thread due to user interrupt")
                break
