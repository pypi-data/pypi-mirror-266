import unittest
from translit_me.transliterator import CharTrie


class TestCharTrie(unittest.TestCase):
    def test_single(self):
        ct = CharTrie()
        ct.add('tom')
        ct.add('er')
        res = ct.get_all()
        print(res)
        self.assertEqual(res, ['tomer'])  # add assertion here

    def test_split(self):
        ct = CharTrie()
        ct.add('tom')
        ct.split(['e', 'a'])
        ct.add('r')
        res = ct.get_all()
        print(res)
        self.assertEqual(res, ['tomer', 'tomar'])  # add assertion here


if __name__ == '__main__':
    unittest.main()
