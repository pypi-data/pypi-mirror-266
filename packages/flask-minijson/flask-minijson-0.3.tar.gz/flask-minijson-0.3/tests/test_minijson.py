import unittest

import minijson

from tests.app import app


class TestMiniJSON(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_minijson(self):
        data = minijson.dumps({'1': '2'})
        resp = self.client.post('/v1', data=data, headers={'Content-Type': 'application/minijson'})
        self.assertEqual(resp.get_json(), {'status': 'ok'})
        resp = self.client.post('/v1', json={'1': '3'})
        self.assertEqual(resp.get_json(), {'status': 'fail'})
