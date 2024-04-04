import unittest

import random_str


class RandomStrTestCase(unittest.TestCase):
    def test_generate_random(self):
        for i in range(4, 128):
            data_1 = random_str.generate_random_str(i)
            print('random data_1', data_1)
            data_2 = random_str.generate_random_str(i)
            print('random data_2', data_2)
            self.assertTrue(data_1 != data_2)
            self.assertTrue(len(data_1) == i)
            self.assertTrue(len(data_2) == i)


if __name__ == '__main__':
    unittest.main()
