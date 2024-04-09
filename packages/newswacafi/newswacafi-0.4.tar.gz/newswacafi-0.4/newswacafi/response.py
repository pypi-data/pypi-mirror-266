from dataclasses import dataclass

@dataclass
class NewswacafiNews:
    Title: str
    title: str
    date: str
    country: str
    countrysort: str
    description: str
    content: str
    category: str
    comments: str
    ncomments: str
    link: str
    username: str
    name: str
    userid: str
    source: str
    urlimage: str
    mentions: str

@dataclass
class NewsWacafiResponse:
    status: str
    data: list[NewswacafiNews]



