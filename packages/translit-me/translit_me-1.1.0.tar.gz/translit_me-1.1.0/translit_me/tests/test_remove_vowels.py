import unittest
from translit_me.transliterator import remove_vowels as rv
from translit_me.lang_tables import *


class TestVowelRemover(unittest.TestCase):
    def test_hebrew(self):
        names = ['נועַם שגיא', "מאנץ'", "בישינה", "דימונה"]
        expected = ['נעם שג', "מנץ'", "בשנ", "דמנ"]
        res = []
        for name in names:
            res.append(rv(name, heb_vowels))
        print(res)
        self.assertListEqual(res, expected)

    def test_english(self):
        names = ['noam sagi', "manch'", "isengard"]
        expected = ['nm sg', "mnch'", 'isngrd']
        res = []
        for name in names:
            res.append(rv(name, en_vowels))
        print(res)
        self.assertListEqual(res, expected)

    def test_arabic(self):
        names = ['دَنْضِيل', "هُرْمُز اَرْداشير"]
        expected = ['دَنْضِيل', 'هُرْمُز اَرْداشير']
        res = []
        for name in names:
            res.append(rv(name, en_vowels))
        print(res)
        self.assertListEqual(res, expected)


if __name__ == '__main__':
    unittest.main()
