def heh_ar(word, position):
    """
    Exception function for the letter heh in Hebrew.
    If at the end of the word, then use Ta Marbuta instead of Ta
    :param word: for testing if the letter is at the end
    :param position: for testing if the letter is at the end
    :return: Ta or Ta Marbuta
    """
    return 'ة' if position == len(word) - 1 else 'ه'


def heh_en(word, position):
    """
    Exception function for the letter heh in Hebrew.
    If at the end of the word, then use 'a' instead of 'h'
    :param word: for testing if the letter is at the end
    :param position: for testing if the letter is at the end
    :return: h or [a, e]
    """
    return ['a', 'e'] if position == len(word) - 1 else 'h'

def s_de_he(word, position):
    """
    Exception function for s in German to hebrew transliteration.
    If the following letter is t or p return ש otherwise return ז
    :param word:
    :param position:
    :return:
    """
    # if last letter in word, return 'ז'
    if position == len(word) - 1:
        return 'ז'

    # check exception rule
    return 'ש' if word[position + 1] in ['t', 'p'] else 'ז'

# Set of final letter exception functions for Arabic --> Hebrew
def fin_kaf_ar(word, position):
    return ['ּך', 'ק'] if position == len(word) - 1 else ['כּ', 'ק']


def fin_mem_ar(word, position):
    return 'ם' if position == len(word) - 1 else 'מ'


def fin_nun_ar(word, position):
    return 'ן' if position == len(word) - 1 else 'נ'


def fin_zad_ar(word, position):
    return 'ץ' if position == len(word) - 1 else 'צ'

def fin_zad_de(word, position):
    return 'ץ' if position == len(word) - 2 else 'צ'

def fin_zhad_ar(word, position):
    return "ץ'" if position == len(word) - 1 else "צ'"


def fin_peh_ar(word, position):
    return 'ף' if position == len(word) - 1 else 'פ'


def hamza_ya(word, position):  # Hamza is pronounced like Ya
    return 'י' if word[position - 1] == 'ا' else 'א'


def fin_a(word, position):
    return 'ה' if position == len(word) - 1 else ''


HE_AR = {"א": "ا", "ב": "ب", "בּ": "ب", "ג": "چ", "ג'": "ج", "ד": ["د", "ض"], "ד'": "ذ", "ה": heh_ar, "ו": "و",
         "ז": "ز",
         "ח": "ح", "ח'": "خ", "ט": ["ط", "ظ"], "י": "ي", "כּ": "ك", "ךּ": "ك", "כ": "ك", "ך": "ك", "ל": "ل", "מ": "م",
         "ם": "م", "נ": "ن",
         "ן": "ن",
         "ס": "س", "ע": "ع", "ע'": "غ", "פ": "ف", "ף": "ف", "פּ": "ب", "ףּ": "ب", "צ": "ص", "ץ": "ص", "צ'": "ض",
         "ץ'": "ض", "ק": "ق", "ר": "ر", "ש": ["ش", "س"], "ת": "ت", "ת'": "ث", "ָ": "َ", "ַ": "َ", "ִ": "ِ", "ֻ": "ُ",
         "וּ": "ُ", "-": "-", "'": "", "]": "", "׳": "", "[": "",
         "ְ": "ْ"}
# Done: duplicate key  "ד":"ض",
# Done: duplicate key "ט":"ظ",
# Done: Differ between dagesh kal and dagesh hazak
# Done: handle Shin/Sin markings if exist
# Done: handle Kamatz vowel

# TODO New rule for ئ - if follows an א then only add י and not אי
AR_HE = {"ال": "אל", "ا": "א", "إ": "א", "أ": "א", "آ": "א", "ب": "בּ", "چ": "ג", "ج": "ג'", "ؤ": "או", "ئ": hamza_ya,
         "ح": "ח", "خ": "ח'",
         "د": "ד", "ذ": "ד'", "ه": "ה", "ة": "ה", "ز": "ז", "ر": "ר", "ت": "ת", "ث": "ת'", "ط": "ט", "ظ": "ט'",
         "س": "ס", "ش": "ש", "ع": "ע", "غ": "ע'", "ص": fin_zad_ar, "ض": fin_zhad_ar, "ف": fin_peh_ar, "پ": "פּ",
         "ق": "ק", "ك": fin_kaf_ar, "ل": "ל", "م": fin_mem_ar, "ن": fin_nun_ar, "ي": "י", "ى": "א", "ء": "א",
         "و": "ו", "َ": "ַ", "ِ": "ִ", "ُ": ["ֻ", "וּ"], "ْ": "ְ"}
# Done: duplicate key, "ُ": "וּ"
# Done: Add final letter rule for סופיות

# Done: add he/ar vowels
HE_EN = {"א": ["a", "ā", "e"], "או": ["ū", "o", "u"], "אי": ["ʾI", "I"], "ב": ["b", "v"], "בּ": "b", "ג": "g",
         "ג'": ["g", "j"], "ד": ["d", "ḍ"], "ד'": "dh", "ה": heh_en, "ו": ["u", "o"], "ז": ["z", "s"], "ח": "ḥ",
         "ח'": "kh", "ט": ["t", "ṭ"], "י": "ī", "כ": ["k", "c", "q"], "ך": "kh", "ל": "l", "מ": "m", "ם": "m", "נ": "n",
         "ן": "n", "ס": "s", "ע": "ʿ", "ע'": "gh", "פ": ["f", "p"], "ף": "f", "פּ": "p", "ףּ": "p",
         "צ": ["ṣ", "ts", "z"], "ץ": ["ṣ", "ts", "z"], "ז'": ["ẓ", "z", "s"], "צ'": ["ḍ", "ch"], "ץ'": ["ḍ", "ch"],
         "ק": ["k", "q", "c"], "ר": "r", "ש": ["ṣ", "sh"], "ת": "t", "ת'": ["th", "ẓ"], "ַ": "a", "ִ": "i", "ֻ": "u",
         "-": "-", "'": "", "]": "", "׳": "", "[": "",
         "וּ": "u"}

AR_EN = {"ال": "al", "ة": "ah", "ع": "ʿ", "طّ": "ṭṭ", "غ": "gh", "ش": "sh", "ذ": "dh", "خ": "kh", "ث": "th", "ص": "ṣ",
         "ئ": "'ī", "ؤ": "'ū",
         "د": "d", "ا": "ā", "و": "ū", "أ": "a", "آ": "ʼā", "ب": "b", "ت": "t", "پ": "p", "چ": "g", "ه": "h", "ر": "r",
         "ز": "z", "ج": "j", "س": "s", "ض": "ḍ", "ط": "ṭ", "ظ": "ẓ", "ف": "f", "ق": "q", "ك": "k", "ل": "l", "م": "m",
         "ن": "n", "ح": "ḥ", "ي": "ī", "إ": ["ʾi", "ī"], "ى": "a", "ء": "ʾ", "َ": "a", "ِ": "i", "ُ": "u", "ْ": "ʼ"}

DE_HE = {"A": "א", "a": fin_a, "b": "ב", "c": ["צ", "ק", "כ"], "d": "ד", "E": "א", "e": fin_a, "f": "פ", "g": "ג", "h": "ה", "i": "י",
         "j": "י", "k": "ק", "l": "ל", "m": fin_mem_ar, "n": fin_nun_ar, "o": "ו", "p": fin_peh_ar, "q": "ק", "r": "ר", "S": "ז", "s": s_de_he,
         "t": ["ת","ט"], "u": ["ו", "י"], "v": ["ו", "פ"], "w": "ו", "x": ["קס", "כס"], "y": "וּ", "z": fin_zad_ar, "ä": "א", "ö": "ו", "ü": "ו",
         "ß": "ס", "eo": "או", "ei": "יי", "ch": fin_kaf_ar, "sch": "ש", "nn": fin_nun_ar, "mm": fin_mem_ar, "pp": "פ", "ßß": "ס", "ie": "י",
         "B": "ב", "C": ["צ", "ק", "כ"], "D": "ד", "F": fin_peh_ar, "G": "ג", "H": "ה", "I": "י", "J": "י", "K": "ק", "L": "ל", "M": fin_mem_ar,
         "N": fin_nun_ar, "O": "או", "P": fin_peh_ar, "Q": "ק", "R": "ר", "T": ["ת","ט"], "U": "ו", "V": ["ו", "פ"], "W": "ו",
         "X": ["קס", "כס"], "Y": "וּ", "Z": fin_zad_ar, "Ä": "א", "Ö": "ו", "Ü": "ו", "ẞ": "ס", "tz": fin_zad_de, "ll":"ל", "Au":"או", "au":"או" ,
         "ia": "יא", "äu": "וי", "eu": "וי", "Sch": "ש", "-": "-", "tt": "ט", "tsch": "טש"}


def non_vowel_at_start(word, position):  # Vav at the beginning of a word is pronounced like V. Otherwise like o or u
    if len(word) > 0 and position == 0:
        return False
    return True


def vowel_at_end(word, position):  # Heh at the end of a word is not pronounced
    if len(word) > 1 and position == len(word) - 1:
        return True
    return False


heb_vowels = {"א": non_vowel_at_start, "וּ": True, "ו": non_vowel_at_start, "י": non_vowel_at_start, "ה": vowel_at_end,
              "ַ": True, "ִ": True, "ֻ": True}
ar_vowels = {"ي": True, "ى": True, "ء": True, "و": non_vowel_at_start, "َ": True, "ِ": True, "ُ": True, "ْ": True}
en_vowels = {"o": non_vowel_at_start, "u": non_vowel_at_start, "O": non_vowel_at_start, "U": non_vowel_at_start
    , "a": non_vowel_at_start, "e": non_vowel_at_start, "i": non_vowel_at_start}

table_lookup = {('he', 'ar'): HE_AR, ('ar', 'he'): AR_HE, ('he', 'en'): HE_EN, ('ar', 'en'): AR_EN, ('de', 'he'): DE_HE,
                'he': heb_vowels, 'ar': ar_vowels, 'en': en_vowels}
