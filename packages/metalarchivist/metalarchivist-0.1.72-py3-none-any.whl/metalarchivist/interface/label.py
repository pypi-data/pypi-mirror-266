
import lxml.html
from dataclasses import dataclass, field, InitVar


@dataclass
class LabelLink:
    name: str = field(init=False)
    link: str = field(init=False)

    def __init__(self, html: str):
        html_anchor = lxml.html.fragment_fromstring(html)
        self.name = html_anchor.text
        self.link = html_anchor.attrib['href']


@dataclass
class LabelProfile:
    url: str
    html: InitVar[bytes]

    def __post_init__(self, profile_html: bytes):
        name: str = field(init=False)
        metallum_id: int = field(init=False)

