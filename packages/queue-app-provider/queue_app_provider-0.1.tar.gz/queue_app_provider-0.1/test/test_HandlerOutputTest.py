import unittest
from unittest.mock import patch, MagicMock

from queue_app_provider.HandlerOutput import HandlerOutput


class HandlerOutputTestCase(unittest.TestCase):
    @patch('queue_app_provider.HandlerOutput.requests.post')
    def test_no_success(self, request_mocked):
        mock_response = MagicMock()
        mock_response.status_code = 204
        output = HandlerOutput(success=False, text="error")
        output.notify('http://www.invalid.cll')

        self.assertEqual('http://www.invalid.cll', request_mocked.call_args[0][0])
        # Es un objeto JSON directamente
        send = request_mocked.call_args[1]
        self.assertEqual(send['json']['success'], False)
        self.assertIsNotNone(send['json']['error'])
        self.assertEqual(send['json']['error'], 'error')

    @patch('queue_app_provider.HandlerOutput.requests.post')
    def test_success(self, request_mocked):
        mock_response = MagicMock()
        mock_response.status_code = 204
        output = HandlerOutput(success=True, text="success")
        output.notify('http://www.invalid.cll')

        self.assertEqual('http://www.invalid.cll', request_mocked.call_args[0][0])
        # Es un objeto JSON directamente
        send = request_mocked.call_args[1]
        self.assertEqual(send['json']['success'], True)
        self.assertIsNotNone(send['json']['data'])
        self.assertEqual(send['json']['data'], 'success')


if __name__ == '__main__':
    unittest.main()
