import re
import sys

from datetime import datetime
from dataclasses import field, InitVar, dataclass

import lxml.html

from .base import Page, Pages, PageDataType

from .band import BandLink
from .album import AlbumLink, _parse_release_date
from .genre import Subgenres
from .label import LabelLink



@dataclass
class Label(PageDataType):
    label: LabelLink

    specialisation: str
    status: str
    website: str
    has_shop: bool


@dataclass
class Labels(list, PageDataType):
    label_page_record: InitVar[list[str]]

    def __post_init__(self, label_page_record: list[str]):
        (edit_link, label_link_text, specialisation, status_text, 
         country, website_link, has_shop_text) = label_page_record
        


@dataclass
class BandGenre(PageDataType):
    profile_url: InitVar[str]
    band_key: str = field(init=False)
    metallum_id: int = field(init=False)
    band: str
    subgenre: str
    genre: str

    def __post_init__(self, profile_url: str):
        metallum_id = profile_url.split('/')[-1]
        self.metallum_id = int(metallum_id)
        self.band_key = metallum_id + '-' + str(hash(self.band) % 2**sys.hash_info.width)


@dataclass
class BandGenres(list, PageDataType):
    genre_page_record: InitVar[list[str]]
    genre: str = field(kw_only=True)

    def __post_init__(self, genre_page_record: list[str]):
        profile_anchor_text, _, subgenre, _ = genre_page_record

        profile_anchor = lxml.html.fragment_fromstring(profile_anchor_text)
        profile_link = profile_anchor.attrib['href']
        band = ''.join(profile_anchor.xpath('./text()'))

        subgenre = subgenre.replace(' Metal', '').strip()
        self.append(BandGenre(profile_link, band, subgenre, self.genre))


@dataclass
class AlbumRelease(PageDataType):    
    band: BandLink
    album: AlbumLink

    release_type: str
    genres: Subgenres
    release_date_display: InitVar[str]
    added_date_display: InitVar[str | None] = field(default=None)

    release_date: str = field(init=False)
    added_date: str | None = field(init=False)

    def __post_init__(self, release_date_display, added_date_display):
        self.release_date = _parse_release_date(release_date_display)

        if added_date_display == 'N/A' or added_date_display is None:
            self.added_date = None
        else:
            added_date = re.sub(r'\/(\d)\/', '/0\1/', added_date_display)
            self.added_date = datetime.strptime(added_date, '%Y-%m-%d %H:%M:%S') \
                                      .strftime('%Y-%m-%dT%H:%M:%SZ')


@dataclass
class AlbumReleases(list, PageDataType):
    release_page_record: InitVar[list[str]]

    def __post_init__(self, release_page_record: list[str]):
        band_link_text, album_link_text, release_type, genres, *dates = release_page_record
        album_link = AlbumLink(album_link_text)

        if re.search(r'>\s?\/\s?<', band_link_text):
            band_links = band_link_text.split(' / ')
            genre_list = genres.split(' | ')

            for link, genre in zip(band_links, genre_list):
                band_link = BandLink(link)
                subgenres = Subgenres(genre)
                album_release = AlbumRelease(band_link, album_link, release_type, subgenres, *dates)
                self.append(album_release)

        else:
            band_link = BandLink(band_link_text)
            subgenres = Subgenres(genres)
            album_release = AlbumRelease(band_link, album_link, release_type, subgenres, *dates)
            self.append(album_release)


class LabelPage(Page, data_type=Labels):
    ...


class LabelPages(Pages, data_type=LabelPage):
    ...


class GenrePage(Page, data_type=BandGenres):
    ...


class GenrePages(Pages, data_type=GenrePage):
    ...


class ReleasePage(Page, data_type=AlbumReleases):    
    ...


class ReleasePages(Pages, data_type=ReleasePage):
    ...
