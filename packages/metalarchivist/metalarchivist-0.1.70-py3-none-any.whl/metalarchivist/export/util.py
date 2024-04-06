import os
import re
import warnings
import json
import time
import random
from datetime import datetime
from urllib.parse import urlencode
from typing import Callable

import urllib3


def normalize_keyword_casing(dictionary: dict):
    def normalize_to_snakecase(match: re.Match):
        preceding_text = match.group(1)
        text = match.group(2).lower()

        if preceding_text == '':
            return text

        return f'{preceding_text}_{text}'

    camel_case = re.compile(r'(\b|[a-z])([A-Z])')

    return {camel_case.sub(normalize_to_snakecase, k): v
            for k, v in dictionary.items()}



class DecodeErrorWarning(UserWarning):
    ...


class MetalArchivesError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code

    def __repr__(self):
        return self.__name__ + f'<{self.status_code}>'
    

class JSONError(MetalArchivesError):
    ...


def perform_request(func: Callable[..., urllib3.BaseHTTPResponse], error, *args, **kwargs) -> urllib3.BaseHTTPResponse:
    attempt = 0
    
    while True:
        attempt += 1
        response = func(*args, **kwargs)
        status_code = response.status

        if status_code == 520:
            time.sleep(30 * attempt)
            continue
        
        elif status_code == 429:
            time.sleep(10 * attempt)
            continue

        elif status_code != 200:
            raise error(status_code)
        
        break

    return response


def get_json(endpoint: str, timeout: urllib3.Timeout, retries=3, user_agent=None) -> dict:
    response = perform_request(MetalArchives.get_page, JSONError, endpoint, timeout=timeout, retries=retries, user_agent=user_agent)

    try:
        response_text = response.data.decode('utf-8', 'replace')
        response_json = json.loads(response_text)
    except json.decoder.JSONDecodeError as e:
        response_text = response_text[:e.pos] + Constant.ERROR_PLACEHOLDER + response_text[e.pos + 1:]
        response_json = json.loads(response_text)

        error_message = f'JSONDecodeError at char {e.pos} of {endpoint}'
        response_json['error'] = error_message
        warnings.warn(error_message, DecodeErrorWarning)
    
    finally:
        return response_json



class Constant:
    ERROR_PLACEHOLDER = '«error»'


class UserAgent:
    user_agent_path = os.path.join(os.path.dirname(__file__), 'user-agents.json')

    @classmethod
    def load(cls) -> list[str]:
        with open(cls.user_agent_path, 'r') as ua_file:
            user_agents = json.load(ua_file)

        return [record['ua'] for record in user_agents]

    @classmethod
    def select(cls, randomize=False) -> str:
        if randomize:
            return random.choice(cls.load())
        
        return 'metalarchivist'


class MetalArchives:
    ROOT = 'https://www.metal-archives.com'
    SEARCH = 'https://www.metal-archives.com/search/advanced/searching/bands'
    BAND_LINKS = 'https://www.metal-archives.com/link/ajax-list/type/band/id'
    GENRE = 'https://www.metal-archives.com/browse/ajax-genre/g'

    @classmethod
    def get_page(cls, url: str, user_agent: str | None = None, 
                 retries: int | None = None, 
                 timeout: urllib3.Timeout | None = None):
        
        if user_agent is None:
            user_agent = UserAgent.select()

        return urllib3.request('GET', url, headers={'User-Agent': user_agent}, retries=retries, timeout=timeout)

    @classmethod
    def genre(cls, genre: str, echo=0, display_start=0, display_length=100):
        genre_endpoint = f'browse/ajax-genre/g/{genre}/json/1'
        return (f'{os.path.join(cls.ROOT, genre_endpoint)}'
                f'?sEcho={echo}&iDisplayStart={display_start}&iDisplayLength={display_length}')

    @classmethod
    def upcoming_releases(cls, echo=0, display_start=0, display_length=100,
                          from_date=datetime.now().strftime('%Y-%m-%d'), 
                          to_date='0000-00-00'):

        return (f'{os.path.join(cls.ROOT, "release/ajax-upcoming/json/1")}'
                f'?sEcho={echo}&iDisplayStart={display_start}&iDisplayLength={display_length}'
                f'&fromDate={from_date}&toDate={to_date}')

    @classmethod
    def search_query(cls, band_name=None, genre=None, country=None, location=None, 
                     themes=None, label_name=None, notes=None, status=None, 
                     year_from=None, year_to=None):
        """
        ?bandNotes=&status=&themes=&location=&bandLabelName=#bands
        """
        query_params = {'exactBandMatch': 1, 'bandName': band_name, 'genre': genre,
                        'country': country, 'status': status, 'location': location,
                        'bandNotes': notes, 'themes': themes, 'bandLabelName': label_name,
                        'yearCreationFrom': year_from, 'yearCreationTo': year_to}
        
        query_str = urlencode({k: v for k, v in query_params.items() if v is not None})

        return query_str
    
    @classmethod
    def links_query(cls, metallum_id: int) -> str:
        return os.path.join(cls.BAND_LINKS, str(metallum_id))