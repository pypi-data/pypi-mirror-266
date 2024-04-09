from datetime import datetime
from dataclasses import asdict

from .export import Band, Album, Genre

Series = list[str | int | float]
Record = dict[str, str | float | int | list]
Dataset = list[Record]


def series(from_list, column) -> Series:
    return [[v for k, v in d.items() if k == column].pop() for d in from_list]


def select(from_list, column) -> Dataset:
    return list(map(lambda n: {column: n[column]}, from_list))


def expand(from_list, column) -> Dataset:
    return list(map(lambda n: dict(**n[column]), from_list))


def drop(from_list, *columns) -> Dataset:
    return [{k: v for k, v in d.items() if k not in columns} for d in from_list]


def rename(from_list, column_map: dict) -> Dataset:
    return [{column_map.get(k, k): v for k, v in d.items()} for d in from_list]


def join(first_list: Dataset, second_list: Dataset, on_column: str) -> Dataset:
    return [dict(**left, **{k: v for k, v in right.items() if k not in left}) 
            for left in first_list for right in second_list 
            if left[on_column] == right[on_column]]


def get_bands(profile_urls: list[str], wait=3.) -> Dataset:
    band_profile = Band.get_profiles(profile_urls, wait=wait)
    band_profile = list(map(lambda n: n.to_dict(), band_profile))
    
    band_desc = expand(select(band_profile, 'description'), 'description')
    band_desc = drop(band_desc, 'genre', 'themes', 'lyrical_themes')

    band_ids = series(band_profile, 'metallum_id')
    band_ids = [int(band_id) for band_id in band_ids]
    band_links = Band.get_profiles_links(band_ids, wait=wait)
    band_links = list(map(asdict, band_links))

    genres = expand(select(band_profile, 'genres'), 'genres')
    themes = expand(select(band_profile, 'themes'), 'themes')

    band_profile = drop(band_profile, 'genres', 'themes',  'description')
    band_profile = join(band_profile, band_links, 'metallum_id')

    band_zip = zip(band_profile, band_desc, genres, themes)

    return [dict(**bp, **bd, **g, **t) for bp, bd, g, t in band_zip]


def get_albums(range_start: datetime | None = None, range_stop: datetime | None = None, 
               wait=3., retries=3, timeout=3.) -> Dataset:
    if range_start:
        release_page = Album.get_range(range_start, range_stop, wait=wait, retries=retries, 
                                       timeout_cxn=timeout, timeout_read=timeout * 3)
    else:
        release_page = Album.get_upcoming(wait=wait, retries=retries, timeout_cxn=timeout, 
                                          timeout_read=timeout * 3)

    release = list(map(asdict, release_page.data))

    # hoist out the link attributes from each band
    profile_urls = select(expand(select(release, 'band'), 'band'), 'link')
    profile_urls = series(profile_urls, 'link')
    profile_urls = [str(p) for p in profile_urls]

    band = get_bands(profile_urls, wait=wait)

    album = expand(select(release, 'album'), 'album')
    album = rename(album, dict(name='album', link='album_url'))

    band = rename(band, dict(url='band_url', name='band'))
    release = drop(release, 'genres', 'band', 'album')
    profile_urls = [dict(band_url=u) for u in profile_urls]
    album_zip = zip(album, profile_urls, release)

    album = [dict(**a, **u, **r) for a, u, r in album_zip]

    return join(album, band, 'band_url')


def get_genres():
    ...
