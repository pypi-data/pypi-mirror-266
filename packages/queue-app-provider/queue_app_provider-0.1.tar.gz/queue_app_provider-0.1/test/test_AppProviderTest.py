import unittest
from time import sleep
from unittest.mock import patch, MagicMock

import werkzeug.exceptions
from werkzeug.datastructures import FileStorage

from queue_app_provider.AppProvider import AppProvider
from queue_app_provider.InputEntry import InputEntry


class AppProviderTest(unittest.TestCase):
    # Test básico en el que no mandamos ni ficheros ni nada y entonces
    # tenemos un error 404
    def test_process_fail(self):

        def process(file):
            return

        app_provider = AppProvider(handler=process)
        request_mock = MagicMock()
        request_mock.files = {}
        request_mock.form = {}
        try:
            app_provider.process(request_mock)
            self.assertFalse(True)
        except werkzeug.exceptions.NotFound:
            self.assertTrue(True)
        finally:
            app_provider.shutdown()

    # Test básico en el que mandamos un fichero y un callback pero el content-type
    # no es correcto
    def test_process_bad_content_type(self):
        def process(file):
            return

        app_provider = AppProvider(handler=process)
        request_mock = MagicMock()
        request_mock.files = {'file': FileStorage(filename='demo.pdf', name='juan.pdf', content_type='application/pdf')}
        request_mock.form = {'callback': 'http://www.callback.url'}
        try:
            app_provider.process(request_mock)
            self.assertFalse(True)
        except werkzeug.exceptions.NotFound:
            self.assertTrue(True)
        finally:
            app_provider.shutdown()

    # Ahora mandamos un ContentType correcto, en la espera que vaya bien, no queremos
    # emular el comportamiento del QueueThread puesto que ya esta contemplado en otro
    # test, solo esperar una respuesta 204
    def test_ok(self):
        def process(file):
            return

        with patch.object(InputEntry, 'handle', return_value='None'):
            app_provider = AppProvider(handler=process, timeout=0.5)
            request_mock = MagicMock()
            request_mock.files = {'file': FileStorage(filename='demo.pdf', name='juan.png', content_type='image/jpg')}
            request_mock.form = {'callback': 'http://www.callback.url'}
            try:
                result = app_provider.process(request_mock)
                self.assertEqual(result[1], 204)
                sleep(2)
            finally:
                app_provider.shutdown()


if __name__ == '__main__':
    unittest.main()
