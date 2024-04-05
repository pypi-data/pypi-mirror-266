
# standard
import json
import time
import calendar
import concurrent.futures
from datetime import datetime

# third-party
import urllib3

# local
from .util import MetalArchives, get_json, normalize_keyword_casing, perform_request
from ..interface import AlbumProfile, ReleasePage, ReleasePages


class AlbumError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code

    def __repr__(self):
        return self.__name__ + f'<{self.status_code}>'


class Album:

    @staticmethod
    def get_profile(profile_url: str) -> AlbumProfile:
        response = perform_request(MetalArchives.get_page, AlbumError, profile_url)
        return AlbumProfile(profile_url, response.data)
    
    @classmethod
    def get_profiles(cls, profile_urls: list[str], segment_size=16) -> list[AlbumProfile]:
        profiles = list()
        profile_urls_len = len(profile_urls)

        with concurrent.futures.ThreadPoolExecutor() as executor:

            # don't throw them all in at once
            for segment_start in range(0, profile_urls_len + segment_size, segment_size):
                segment_end = min(segment_start + segment_size, profile_urls_len)

                # feed the beast
                album_futures = (executor.submit(cls.get_profile, url) 
                                 for url in profile_urls[segment_start:segment_end])

                # examine the remains
                for future in concurrent.futures.as_completed(album_futures):
                    profile = future.result()
                    profiles.append(profile)
        
        return profiles

    @staticmethod
    def get_upcoming(echo=0, page_size=100, wait=3., retries=3) -> ReleasePage:
        data = ReleasePages()
        record_cursor = 0
        timeout = urllib3.Timeout(connect=3.0, read=9.0)

        while True:
            endpoint = MetalArchives.upcoming_releases(echo, record_cursor, page_size)

            response = get_json(endpoint, timeout, retries)
            releases = ReleasePage(**normalize_keyword_casing(response))

            data.append(releases)

            record_cursor += page_size
            echo += 1

            if releases.total_records - 1 > record_cursor:
                time.sleep(wait)
                continue
            break

        return data.combine()

    @staticmethod
    def get_range(range_start: datetime, range_stop: datetime | None = None,
                  echo=0, page_size=100, wait=3., retries=3) -> ReleasePage:

        data = ReleasePages()
        record_cursor = 0
        timeout = urllib3.Timeout(connect=3.0, read=9.0)

        range_stop_str = range_stop.strftime('%Y-%m-%d') if range_stop is not None else '0000-00-00'

        while True:
            endpoint = MetalArchives.upcoming_releases(echo, record_cursor, page_size,
                                                       range_start.strftime('%Y-%m-%d'),
                                                       range_stop_str)
            
            response = get_json(endpoint, timeout, retries)
            releases = ReleasePage(**normalize_keyword_casing(response))

            data.append(releases)

            record_cursor += page_size
            echo += 1

            if releases.total_records - 1 > record_cursor:
                time.sleep(wait)
                continue
            break

        return data.combine()
    
    @classmethod
    def get_month(cls, year, month) -> ReleasePage:
        first_day, last_day = calendar.monthrange(year, month)
        month_albums = cls.get_range(datetime(year, month, first_day), 
                                     datetime(year, month, last_day))
        
        return month_albums

    @classmethod
    def get_all(cls):
        year_range = range(1970, datetime.now().year + 2)
        months = [(year, month) 
                  for month in range(1, 13) 
                  for year in year_range]
        
        release_pages = ReleasePages(cls.get_month(*n) for n in months)

        return release_pages.combine()

