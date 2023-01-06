"""
This module provides API functionality for yandex lingvo services.
"""

import logging
import os
import string

import pyaspeller
import requests
from dotenv import load_dotenv

from app.templates import MessageTemplate, Translate

logger = logging.getLogger(__name__)

load_dotenv()

YKEY = os.getenv("YKEY")
ENDPOINT = 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup?'


def answer_spellcheck(spellcheck, translate):
    if spellcheck:
        if not spellcheck.correct:
            if spellcheck.spellsafe:
                if translate:
                    return '    _Your request was corrected!_\n' + translate
                return '    _Your request was corrected!_\n'
    return translate


def check_spelling(data):
    try:
        spellcheck = pyaspeller.Word(data)
        if spellcheck.spellsafe:
            data = spellcheck.spellsafe
    except Exception as err:
        logging.exception(str(err))
        spellcheck = None

    return data, spellcheck


def normalize(data):
    warning = True
    if not data:
        return MessageTemplate.EMPTY_REQUEST, warning
    if isinstance(data, list):
        data = ' '.join(data)
    data = str(data).replace('`', '')
    if not data:
        return MessageTemplate.ONLY_TILDE, warning
    else:
        warning = False
        data = data.translate(str.maketrans('', '', string.punctuation))
        return data.lower().strip(), warning


def format_dict_message(data):
    res = ''
    delimiter = '\n'
    nbsp = u'\xa0'
    for _, topic in enumerate(data):
        res += Translate.POS.format(topic['pos'])
        if 'ts' in topic:
            res += Translate.TRANSCRIPTION.format(topic['ts'], delimiter)
        else:
            res += delimiter
        for tr in topic['tr']:
            res += Translate.TRANSLATION.format(nbsps=4 * nbsp, text=tr['text'])
            if 'mean' in tr:
                mean = ''
                for m in tr['mean']:
                    mean += Translate.MEANING_UNIT.format(m=m['text'])
                mean = Translate.MEANING.format(mean.rstrip('; '), delimiter)
                res += mean
            else:
                res += delimiter
            if 'ex' in tr:
                tmp = Translate.EXAMPLE.format(
                    nbsps=8 * nbsp,
                    ex=tr['ex'][0]['text'],
                    ex_tr='/ '.join([etr['text'] for etr in tr['ex'][0]['tr']]),
                    delimeter=delimiter
                )
                res += tmp
    return res


def dicservice_request(src):
    request = requests.compat.urlencode(
        {'key': YKEY, 'lang': 'en-ru', 'text': src})
    logger.info(request)
    return requests.get('{}{}'.format(ENDPOINT, request))


def load_content_from_api(content):
    data = dicservice_request(content)
    json_dump = data.json()
    logger.info(json_dump)
    definition = json_dump['def']
    if not definition:
        return
    return format_dict_message(definition)
