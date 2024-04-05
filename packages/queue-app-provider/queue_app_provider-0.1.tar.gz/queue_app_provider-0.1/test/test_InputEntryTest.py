import unittest
from unittest.mock import MagicMock

from werkzeug.datastructures import FileStorage

from queue_app_provider.HandlerOutput import HandlerOutput
from queue_app_provider.InputEntry import InputEntry


class InputEntryTest(unittest.TestCase):
    # El objetivo de este test es verificar el funcionamiento básico del objeto InputEntry,
    # comprobando como 'crea' un fichero temporal y se invoca a la función de callback
    # ante un caso de éxito en la petición.
    def test_Entry(self):
        storage = FileStorage(filename='sample.jpg', name='demo', content_type='image/jpg')
        # Activamos el mock, para que save no haga en realidad "nada"
        storage.save = MagicMock()
        filename = ''
        callback = ''

        def handler(file):
            nonlocal filename
            filename = file
            output = HandlerOutput(success=True, text='Demo')

            def side_effect(arg):
                nonlocal callback
                callback = arg
            output.notify = MagicMock(side_effect=side_effect)
            return output

        entry = InputEntry(storage, 'http://www.inexistant.domain')
        entry.handle(handler)

        self.assertNotEqual(filename, '')
        self.assertEqual(callback, 'http://www.inexistant.domain')


if __name__ == '__main__':
    unittest.main()
