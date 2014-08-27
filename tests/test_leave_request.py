from tests.server import TestServer


class TestLeaveRequest(TestServer):
    def _test_error(self, response):
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 1)
        self.assertFalse(response['leave']['ok'])

    def test_not_joined(self):
        self._test_error(self._request({'leave': None}))
