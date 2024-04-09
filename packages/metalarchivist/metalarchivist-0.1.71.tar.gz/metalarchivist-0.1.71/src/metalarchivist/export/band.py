import time
import concurrent.futures

from .util import MetalArchives, MetalArchivesError, perform_request
from ..interface import BandProfile, BandExternalLinks, SearchResults


class BandError(MetalArchivesError):
    ...


class Band:

    @staticmethod
    def search_profile(band_name: str, user_agent: str | None = None, **kwargs) -> SearchResults:
        query_str = MetalArchives.search_query(band_name=band_name, **kwargs)
        search_url = MetalArchives.SEARCH + '?' + query_str
        response = perform_request(MetalArchives.get_page, BandError, search_url, user_agent=user_agent)
        return SearchResults(search_url, response.data)
    
    @staticmethod
    def get_profile(profile_url: str, user_agent: str | None = None) -> BandProfile:
        response = perform_request(MetalArchives.get_page, BandError, profile_url, user_agent=user_agent)
        return BandProfile(profile_url, response.data)
    
    @staticmethod
    def get_profile_links(metallum_id: int, user_agent: str | None = None) -> BandExternalLinks:
        links_url = MetalArchives.links_query(metallum_id)
        response = perform_request(MetalArchives.get_page, BandError, links_url, user_agent=user_agent)
        return BandExternalLinks(metallum_id, response.data)
    
    @staticmethod
    def _get_profiles_thread(profile_url: str) -> BandProfile:
        response = perform_request(MetalArchives.get_page, BandError, profile_url)
        return BandProfile(profile_url, response.data)

    @staticmethod
    def _get_links_thread(metallum_id: int) -> BandExternalLinks:
        links_url = MetalArchives.links_query(metallum_id)
        response = perform_request(MetalArchives.get_page, BandError, links_url)
        return BandExternalLinks(metallum_id, response.data)

    @classmethod
    def get_profiles(cls, profile_urls: list[str], segment_size=8, wait=3.) -> list[BandProfile]:

        profile_urls_len = len(profile_urls)
        profiles = list()
        
        if profile_urls_len == 0:
            return profiles

        with concurrent.futures.ThreadPoolExecutor() as executor:
            
            processed_urls = set()

            # don't throw them all in at once
            for segment_start in range(0, profile_urls_len + segment_size, segment_size):
                segment_end = min(segment_start + segment_size, profile_urls_len)

                band_futures = list()
                for url in profile_urls[segment_start:segment_end]:
                    if url not in processed_urls:
                        future = executor.submit(cls._get_profiles_thread, url)
                        band_futures.append(future)
                        processed_urls.add(url)
                        time.sleep(wait)

                # examine the remains
                for future in concurrent.futures.as_completed(band_futures):
                    profile = future.result()
                    profiles.append(profile)

        return profiles
    
    @classmethod
    def get_profiles_links(cls, metallum_ids: list[int], segment_size=8, wait=3.) -> list[BandExternalLinks]:

        links = list()
        metallum_ids_count = len(metallum_ids)

        if metallum_ids_count == 0:
            return links

        with concurrent.futures.ThreadPoolExecutor() as executor:
            
            processed_urls = set()

            # don't throw them all in at once
            for segment_start in range(0, metallum_ids_count + segment_size, segment_size):
                segment_end = min(segment_start + segment_size, metallum_ids_count)

                band_futures = list()
                for url in metallum_ids[segment_start:segment_end]:
                    if url not in processed_urls:
                        future = executor.submit(cls._get_links_thread, url)
                        band_futures.append(future)
                        processed_urls.add(url)
                        time.sleep(wait)

                # examine the remains
                for future in concurrent.futures.as_completed(band_futures):
                    profile = future.result()
                    links.append(profile)
        
        return links
