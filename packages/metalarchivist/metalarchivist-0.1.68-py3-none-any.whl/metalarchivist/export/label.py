import time
import urllib3
import concurrent.futures

from .util import MetalArchives, normalize_keyword_casing, perform_request, ALPHABET
from ..interface import LabelPage, LabelPages, LabelProfile


class LabelError(Exception):
    def __init__(self, status_code, url):
        self.status_code = status_code
        self.url = url

    def __repr__(self):
        return repr(self) + f'<{self.status_code}: {self.url}>'


class Label:
    @classmethod
    def get_label(cls, label_url: str, user_agent: str | None = None):
        response = perform_request(MetalArchives.get_page, LabelError, label_url, user_agent=user_agent)
        return LabelProfile(label_url, response.data)

    @classmethod
    def get_labels_by_letter(cls, letter: str, echo=0, page_size=500, wait=3.) -> LabelPage:
        data = LabelPages()
        record_cursor = 0
        timeout = urllib3.Timeout(connect=3.0, read=9.0)

        while True:
            endpoint = MetalArchives.label_by_letter(letter, echo, record_cursor, page_size)

            response = perform_request(MetalArchives.get_page, LabelError, endpoint, timeout=timeout)
            kwargs = normalize_keyword_casing(response.json())
            label_bands = LabelPage(**kwargs)

            data.append(label_bands)

            record_cursor += label_bands.count
            echo += 1

            if label_bands.total_records > record_cursor:
                time.sleep(wait)
                continue
            
            break

        return data.combine()

    @classmethod
    def get_labels(cls, *letters: str, echo=0, page_size=500, wait=3.) -> LabelPage:
        data = LabelPages()

        if len(letters) == 0:
            letters = tuple([n for n in ALPHABET])

        with concurrent.futures.ThreadPoolExecutor() as executor:
            label_futures = [executor.submit(cls.get_labels_by_letter, letter, echo=echo, page_size=page_size, wait=wait)
                             for letter in letters]
            
            for future in concurrent.futures.as_completed(label_futures):
                data.append(future.result())

        return data.combine()
