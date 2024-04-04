import base64
import binascii
import time
import unittest

import common


@common.timing_decorator
def example_function():
    time.sleep(1)


class CommonTestCase(unittest.TestCase):
    def test_b64_decode(self):
        ret = common.decode_b64_data('')
        self.assertTrue(ret == b'')

        ret = base64.b64encode('hello,world'.encode('utf-8')).decode('utf-8')
        raw = common.decode_b64_data(ret)
        self.assertTrue(raw == 'hello,world'.encode('utf-8'))

        with self.assertRaises(binascii.Error) as e:
            common.decode_b64_data('hello,world')
            self.assertTrue(e == binascii.Error)

    def test_time(self):
        example_function()
        self.assertTrue(1)


if __name__ == '__main__':
    unittest.main()
