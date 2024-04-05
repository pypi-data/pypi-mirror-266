import os
import tempfile
from typing import Callable

from werkzeug.datastructures import FileStorage


# Very simple class, an InputEntry is just a holder for queue entries in our
# processing system.
#
# Since we are working with files, this InputEntry receives a `FileStorage`
# object from the flask request, and dumps original file object to
# a local file. When queue process this entry, handler is called and
# after that the local file is purged from system
#
# Created by: David Rodríguez Alfayate
# Version: 1.0
from queue_app_provider.HandlerOutput import HandlerOutput


class InputEntry:
    def __init__(self, file_storage: FileStorage, callback):
        self.callback = callback
        self.fh, self.file = tempfile.mkstemp()
        file_storage.save(self.file)

    # Temporary file removal
    def clear(self):
        os.close(self.fh)
        os.remove(self.file)

    # Data processing function called from `QueueThread` main queue
    # we just execute the handler method
    def handle(self, handler: Callable[[str], HandlerOutput]):
        # Generamos la salida de la clase, y tenemos con ella
        # que enviar estos datos al sistema de procesado externo
        output = handler(self.file)
        try:
            output.notify(self.callback)
        finally:
            self.clear()
