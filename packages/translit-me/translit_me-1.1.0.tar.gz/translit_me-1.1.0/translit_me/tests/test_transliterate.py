import unittest
import logging
from translit_me.transliterator import transliterate as tr
from translit_me.lang_tables import *
import sys
# sys.stdout.reconfigure(encoding='utf-8')



class TestTransliterate(unittest.TestCase):
    def test_hebrew_arabic(self):
        # This is effective if the output is piped or redirected.
        logging.basicConfig(level=logging.DEBUG, encoding='utf-8')

        names = ['נועַם', "מאנץ'", "בישינה", "דימונה"]
        expected = ['نوعَم', 'مانض', 'بيشينة', 'بيسينة', 'ديمونة', 'ضيمونة']
        res = tr(names, HE_AR)
        logging._defaultFormatter = logging.Formatter(u"%(message)s")
        logging.info(res)
        self.assertListEqual(res, expected)

    def test_arabic_hebrew(self):
        logging.basicConfig(level=logging.DEBUG, encoding='utf-8')

        names = ['نوعَم', 'مانض', 'بيشينة', 'بيسينة', 'ديمونة', 'الجزائر','المؤمنين', 'بئر زمزم']
        expected = ['נועַם', "מאנץ'", 'בּישינה', 'בּיסינה', 'דימונה', "אלג'זאיר", 'אלמאומנין', 'בּאר זמזם']

        res = tr(names, AR_HE)
        logging._defaultFormatter = logging.Formatter(u"%(message)s")
        logging.info(res)
        self.assertListEqual(res, expected)

    def test_hebrew_english(self):
        names = ['נועַם', "מאנץ'", "בישינה"]  # ["מסטראי'",'משתראן']
        # ['כסבין', 'קלש', 'ארמילו', 'אבירו', 'בישינה', 'קדמות', 'לודקיא', 'גרדיגי', 'מיטילין', 'יובשטריסה']

        expected = ['nuʿam', 'noʿam', 'manḍ', 'manch', 'mānḍ', 'mānch', 'menḍ', 'mench', 'bīṣīna', 'bīṣīne', 'bīshīna',
                    'bīshīne', 'vīṣīna', 'vīṣīne', 'vīshīna', 'vīshīne']
        res = tr(names, HE_EN)
        print(res)
        self.assertListEqual(res, expected)

    def test_multi_word(self):
        names = ['כפר סבא', 'כפר סבא רבא', 'בן פורד יוסף']
        expected = ['كفر سبا', 'كفر سبا ربا', 'بن فورد يوسف', 'بن فورض يوسف']
        res = tr(names, HE_AR)
        print(res)
        self.assertListEqual(res, expected)

    def test_de_he(self):
        names = ['Ytzchak Neufeld', 'Deutschkreutz']
        expected = ['וצחק נופלד', 'דויטשקרויץ']
        res = tr(names, DE_HE)
        print(res)
        self.assertListEqual(res, expected)

    def test_for_whg(self):
        def he_en(name, conversion):
            return tr([name], conversion)

        t = he_en("שמורות הפנדה הענק בסצ'ואן", HE_EN)
        len(t)  # 4608


if __name__ == '__main__':
    unittest.main()
