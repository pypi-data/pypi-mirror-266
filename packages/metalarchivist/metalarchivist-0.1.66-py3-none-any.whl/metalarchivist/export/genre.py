import time
import concurrent.futures

import urllib3

from .util import MetalArchives, normalize_keyword_casing, perform_request
from ..interface import Genre, GenrePage, GenrePages


class GenreError(Exception):
    def __init__(self, status_code, url):
        self.status_code = status_code
        self.url = url

    def __repr__(self):
        return repr(self) + f'<{self.status_code}: {self.url}>'


class GenreBands:

    @classmethod
    def get_genre_size(cls, genre: Genre) -> int:
        timeout = urllib3.Timeout(connect=3.0, read=9.0)
        endpoint = MetalArchives.genre(genre.value, display_length=1)
        response = perform_request(MetalArchives.get_page, GenreError, endpoint, timeout=timeout)
        kwargs = normalize_keyword_casing(response.json())
        genre_page = GenrePage(metadata=dict(genre=genre.value), **kwargs)
        return genre_page.total_records

    @staticmethod
    def get_genre(genre: Genre, echo=0, page_size=500, wait=3.) -> GenrePage:
        data = GenrePages()
        record_cursor = 0
        timeout = urllib3.Timeout(connect=3.0, read=9.0)

        genre_page_metadata = dict(genre=genre.value)

        while True:
            endpoint = MetalArchives.genre(genre.value, echo, record_cursor, page_size)

            response = perform_request(MetalArchives.get_page, GenreError, endpoint, timeout=timeout)
            kwargs = normalize_keyword_casing(response.json())
            genre_bands = GenrePage(metadata=genre_page_metadata, **kwargs)
            
            data.append(genre_bands)

            record_cursor += genre_bands.count
            echo += 1
            
            if genre_bands.total_records == record_cursor:
                break
            
            time.sleep(wait)

        return data.combine()
    
    @classmethod
    def get_genres(cls, *genres: Genre, echo=0, page_size=500, wait=3.) -> GenrePage:
        data = GenrePages()

        if len(genres) == 0:
            genres = tuple([g for g in Genre])

        with concurrent.futures.ThreadPoolExecutor() as executor:
            genre_futures = [executor.submit(cls.get_genre, genre, echo=echo, page_size=page_size, wait=wait) 
                             for genre in genres]
        
            for future in concurrent.futures.as_completed(genre_futures):
                data.append(future.result())

        return data.combine()
