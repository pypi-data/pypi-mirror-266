import queue
import threading
import unittest
from time import sleep
from unittest.mock import MagicMock

from werkzeug.datastructures import FileStorage

from queue_app_provider.InputEntry import InputEntry
from queue_app_provider.QueueThread import QueueThread


class QueueThreadTest(unittest.TestCase):
    def test_queue_and_stop(self):
        queue_lock = threading.Event()
        the_queue = queue.Queue()
        local_file = ''

        def handler(file):
            nonlocal local_file
            local_file = file
            return MagicMock()

        queue_thread = QueueThread(event_handler=queue_lock, shared_queue=the_queue, handler=handler, timeout=0.5)
        queue_thread.start()

        # Introducimos algo en la cola y esperamos que este incluido
        storage = FileStorage(filename='sample.jpg', name='demo', content_type='image/jpg')
        # Activamos el mock, para que save no haga en realidad "nada"
        storage.save = MagicMock()

        the_queue.put(InputEntry(storage, 'http://www.naa.es'))
        self.assertTrue(queue_thread.is_alive())

        sleep(2)
        self.assertEqual(the_queue.qsize(), 0)
        self.assertNotEqual(local_file, '')
        self.assertTrue(queue_thread.is_alive())

        queue_lock.set()
        sleep(2)
        self.assertFalse(queue_thread.is_alive())


if __name__ == '__main__':
    unittest.main()
