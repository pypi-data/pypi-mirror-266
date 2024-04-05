
import re

from dataclasses import dataclass, field, asdict, InitVar
from urllib.parse import unquote

import lxml.html
import lxml.etree

from .genre import Subgenres
from .theme import Themes



class InvalidAttributeError(Exception):
    ...


class InvalidPageError(Exception):
    ...


@dataclass
class BandLink:
    """ An HTML anchor tag pointing to a unique band profile """
    name: str = field(init=False)
    link: str = field(init=False)

    def __init__(self, html: str):
        html_anchor = lxml.html.fragment_fromstring(html)
        self.name = html_anchor.text
        self.link = html_anchor.attrib['href']


@dataclass(frozen=True)
class BandMember:
    """ A member of a band """
    alias: str
    role: str
    profile: str = field(hash=True)


@dataclass(frozen=True)
class BandDescription:
    """ Additional information pertaining to a unique band """
    country_of_origin: str = field(kw_only=True)
    location: str = field(kw_only=True)
    status: str = field(kw_only=True)
    formed_in: str = field(kw_only=True)
    genre: str = field(kw_only=True)
    themes: str | None = field(kw_only=True, default=None)
    lyrical_themes: str | None = field(kw_only=True, default=None)
    years_active: str = field(kw_only=True)
    last_label: str | None = field(kw_only=True, default=None)
    current_label: str | None = field(kw_only=True, default=None)



@dataclass
class BandExternalLink:
    """ An HTML anchor tag pointing to a band's profile outside of metal-archives.com """
    name: str
    url: str


@dataclass
class BandExternalLinks:
    """ A collection of profiles pertaining to a single band, defined by metallum_id """

    metallum_id: int
    html: InitVar[bytes]
    links: list = field(init=False)

    def __post_init__(self, links_html: bytes):
        links_document = lxml.html.document_fromstring(links_html)
        anchors: list = links_document.xpath('//table[@id = "linksTablemain"]//td/a')
        
        links = list()
        for link in anchors:
            try:
                links.append(BandExternalLink(link.text.strip(), link.attrib['href']))
            except AttributeError:
                alt_name = link.attrib['title'].replace('Go to:', '').strip()
                links.append(BandExternalLink(alt_name, link.attrib['href']))
        
        self.links = links


@dataclass
class BandLineupCategory:
    """ A unique line-up for a band (e.g. current, past, past (live), etc) """

    name: str
    members: list[BandMember]


@dataclass
class BandProfile:
    """ A unique band's profile page """
    url: str
    html: InitVar[bytes]
    
    name: str = field(init=False)
    metallum_id: int = field(init=False)
    lineup: list[BandLineupCategory] = field(init=False)
    description: BandDescription = field(init=False)
    genres: Subgenres = field(init=False)
    themes: Themes = field(init=False)

    def __post_init__(self, profile_html: bytes):
        self.metallum_id = int(self.url.split('/')[-1])

        profile_document = lxml.html.document_fromstring(profile_html)

        try:
            profile_band_name_xpath = '//h1[@class="band_name"]/a/text()'
            band_name: list = profile_document.xpath(profile_band_name_xpath)

            if len(band_name) == 0:
                profile_band_name_xpath = '//h1[@class="band_name noCaps"]/a/text()'
                band_name: list = profile_document.xpath(profile_band_name_xpath)

            self.name = band_name.pop()

        except IndexError:
            raise InvalidPageError(f'unable to parse band name from {self.url}')

        lineup = self._parse_lineup(profile_document)
        if len(lineup) == 0:
            lineup = self._parse_lineup(profile_document, all_members=False)
        
        self.lineup = lineup

        desc_titles = self._parse_description_titles(profile_document)
        desc_details = self._parse_description_details(profile_document)

        self.description = self._parse_description(desc_titles, desc_details)
        if self.description.themes:
            self.themes = Themes(self.description.themes)
        elif self.description.lyrical_themes:
            self.themes = Themes(self.description.lyrical_themes)
        else:
            self.themes = Themes('Unknown')

        self.genres = Subgenres(self.description.genre)

    @staticmethod
    def _parse_lineup(profile_document, all_members=True) -> list[BandLineupCategory]:
        member_selection = 'band_tab_members_all' if all_members else 'band_tab_members_current'
        lineup_tablerows_xpath = (f'//div[@id="{member_selection}"]'
                                  f'//table[contains(@class, "lineupTable")]'
                                  f'//tr[@class="lineupHeaders" or @class="lineupRow"]')
        
        lineup_tablerows = profile_document.xpath(lineup_tablerows_xpath)

        lineup_dict = dict()
        section_cursor = 'unknown' if all_members else 'current'

        for tablerow in lineup_tablerows:
            
            if tablerow.attrib['class'] == 'lineupHeaders':
                section_cursor = tablerow.xpath('td/text()').pop().strip().lower()
            
            elif tablerow.attrib['class'] == 'lineupRow':
                member_profile_anchor = tablerow.xpath('td[1]/a').pop()
                member_profile = member_profile_anchor.attrib['href']

                try:
                    member_alias = member_profile_anchor.text.strip()
                except AttributeError:
                    member_alias = unquote(member_profile.split('/')[-2])

                member_role = tablerow.xpath('td[2]/text()').pop() \
                                      .strip().replace('\xa0', ' ')

                member = BandMember(member_alias, member_role, member_profile)

                try:
                    lineup_dict[section_cursor.lower()].append(member)
                except KeyError:
                    lineup_dict[section_cursor.lower()] = [member]
            
            else:
                raise InvalidAttributeError

        # TODO: collapse list and dict creation into single loop        
        lineup_list = [BandLineupCategory(category, members)
                       for category, members in lineup_dict.items()]

        return lineup_list
    
    @staticmethod
    def _parse_description_titles(profile_document: lxml.etree.ElementBase) -> list[str]:
        desc_titles_xpath = '//div[@id="band_stats"]/dl/dt//text()'
        desc_titles = profile_document.xpath(desc_titles_xpath)
        desc_titles = [re.sub(r'[^\w\s]+', '', title) for title in desc_titles]
        desc_titles = [re.sub(r'\s+', '_', title).lower() for title in desc_titles]
        return desc_titles

    @staticmethod
    def _parse_description_details(profile_document: lxml.etree.ElementBase) -> list[str]:
        desc_detail_xpath = '//div[@id="band_stats"]/dl/dt/following-sibling::dd'
        desc_detail = profile_document.xpath(desc_detail_xpath)
        desc_detail = [node.xpath('.//text()') for node in desc_detail]
        desc_detail = [''.join(text).replace('\n', ' ').strip() for text in desc_detail]
        desc_detail = ['Unknown' if detail == 'N/A' else detail for detail in desc_detail]

        return desc_detail

    @staticmethod
    def _parse_description(description_titles, description_details) -> BandDescription:
        description = {dt: dd for dt, dd in zip(description_titles, description_details)}
        return BandDescription(**description)
    
    def to_dict(self):
        dictionary = asdict(self)
        dictionary['genres'] = self.genres.to_dict()
        dictionary['themes'] = self.themes.to_dict()
        return dictionary
    