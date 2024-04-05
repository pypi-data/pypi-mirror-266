import queue
import signal
import sys
import threading
from typing import Callable

from flask import Request
from flask import abort

from queue_app_provider.HandlerOutput import HandlerOutput
from queue_app_provider.InputEntry import InputEntry
from queue_app_provider.QueueThread import QueueThread


# This is the main class and the one that should be used from the external flask app,
# it can be configured using the handler (the processor from the input file), timeout
# and accepted content-types for this AppProvider
#
# Created by: David Rodríguez Alfayate
# Version: 1.0
class AppProvider:
    def __init__(self, handler: Callable[[str], HandlerOutput],
                 accepted_types=['image/jpeg', 'image/jpg', 'image/png'], timeout=30):
        self.handler = handler
        # We use this event to stop created thread if needed
        self.event = threading.Event()
        # Accepted mime types
        self.accepted_types = accepted_types

        # Internal queue to store data
        self.queue = queue.Queue()
        # We create processing thread, with global data.
        self.queue_thread = QueueThread(handler=handler, shared_queue=self.queue, event_handler=self.event,
                                        timeout=timeout)
        self.queue_thread.start()

        def stop(signum, frame):
            self.shutdown()
            sys.exit(0)

        # Since this will be used in a flask application, we shall be sure than when a SIGINT or SIGTERM signals
        # are sent, our application is stopped gracefully, that means that the queueThread is properly stopped.
        signal.signal(signal.SIGINT, stop)
        signal.signal(signal.SIGTERM, stop)

    # Shutdown method as used from inner stop function or when invoked from a test case
    def shutdown(self):
        self.event.set()
        self.queue_thread.join()

    # Main processing of request, it verifies that input data is correctly defined, meaning
    # that a file and a callback url is provided, and check if content-type is valid
    # for the intended use-case. If demands are satisfied, a new InputEntry is created and
    # stored in queue.
    # When the request is properly processed we send requester - as soon as possible - a 204
    # if conditions are not satisfied, our response is just a simple 404.
    def process(self, request: Request):
        if 'file' not in request.files.keys() or 'callback' not in request.form.keys():
            abort(404)
        file = request.files['file']
        callback = request.form['callback']
        if not file.filename or not callback or not file.content_type in self.accepted_types:
            abort(404)

        # We create the entry, enqueueing it properly
        entry = InputEntry(file, callback)
        self.queue.put_nowait(entry)

        # Just a no-content response is enough, we are not returning anything especially interesting indeed.
        return "", 204
