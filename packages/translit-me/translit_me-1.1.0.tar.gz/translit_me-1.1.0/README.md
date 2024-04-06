# The MEHDIE Transliteration Service and Python Package

This repository contains the source code for the MEHDIE Transliteration Service and Python package. 
The service is a RESTful API that can be used to transliterate names between Hebrew, Arabic and Latin characters. 
The Python package provides a Python interface to the service.

The service was developed as part of the MEHDIE project- https://mehdie.org/. <img src="https://gitlab.com/m8417/hebrew-transliteration-service/-/raw/main/mehdie_logo.png" alt="the mehdie logo is a line-drawn M in several similar lines symbolizing the similarity and distincness of the middle-eastern languages" width="100"/>)

MEHDIE is funded by the Israel Ministry of Science and Technology [MOST](www.most.gov.il). <img src="https://gitlab.com/m8417/hebrew-transliteration-service/-/raw/main/menora.png" alt="The symbol of the state of Israel, a Menora with two olive branches on the sides." width="80"/>) 

## Installation
You can use the Dockerfile and cloudbuild yaml file to deploy to a cloud run service
or you can use the python package to use the service in your own code.

## Usage

### Python Package - Transliteration

```python
import unittest
from translit_me.transliterator import transliterate as tr
from translit_me.lang_tables import *

class TestTransliterate(unittest.TestCase):
    def test_hebrew_arabic(self):
        names = ['נועַם', "מאנץ'", "בישינה", "דימונה"]
        expected = ['نوعَم', 'مانض', 'بيشينة', 'بيسينة', 'ديمونة', 'ضيمونة']
        res = tr(names, HE_AR)
        print(res)
        self.assertListEqual(res, expected)
```

More examples can be found in the tests folder.

### RESTful API

The service is a RESTful API that can be used to transliterate names between Hebrew, Arabic and Latin characters.

````python
import requests

def transliterate_service(to_transliterate: list,from_lang: str,to_lang: str):
  """
  This method invokes a cloud run service to transliterate a list of strings
  (e.g., ['نوعم', 'مانض', 'پيشينة'])
  from the from_lang (e.g., 'ar') to the to_lang (e.g., 'en').
  Supported languages: ('he','ar','en'). Anything non 'he'/'ar' will be treated
  as 'en'
  """
  url = 'https://hebrew-transliteration-service-snlwejaxvq-ez.a.run.app/'
  args = {'from_lang': from_lang, 'to_lang': to_lang, 'data': to_transliterate}
  x = requests.post(url, json=args)
  res_list = x.json()['transliterations']
  return res_list

names = ["תִפְלִיס","תַרְג'","תַרוּג'ה"]
from_language = 'he'
to_language = 'ar'

transliterate_service(names, from_language, to_language)
````

