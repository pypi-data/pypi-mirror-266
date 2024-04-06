import json
from json import JSONEncoder

from fastapi import FastAPI, Request, Response

from transliterator import transliterate, remove_vowels as rv
from lang_tables import *

app = FastAPI()

lang_tables = {('he', 'ar'): HE_AR, ('ar', 'he'): AR_HE, ('he', 'en'): HE_EN, ('ar', 'en'): AR_EN, ('de', 'he'): DE_HE}


@app.post("/")
async def home(request: Request):
    body = await request.json()
    # ToDo tests input for type list
    # ToDo tests input for language
    from_lang = body['from_lang']
    to_lang = body['to_lang']
    # ToDo tests existing table for requested lang pair
    table = lang_tables[(from_lang, to_lang)]
    res = transliterate(body['data'], table)
    print('[INFO] transliteration result: {}'.format(res))
    json_str = json.dumps({"transliterations": res}, cls=JSONEncoder).encode('utf-8')
    return Response(media_type="application/json", content=json_str)


@app.post("/remove_vowels")
async def home(request: Request):
    body = await request.json()
    # ToDo tests input for type list
    # ToDo tests input for language
    from_lang = body['lang']
    # ToDo tests existing table for requested lang pair
    table = table_lookup[from_lang]
    res = []
    for name in body['data']:
        res.append(rv(name, table))
    print('[INFO] vowel removal result: {}'.format(res))
    json_str = json.dumps({"names": res}, cls=JSONEncoder).encode('utf-8')
    return Response(media_type="application/json", content=json_str)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app)
