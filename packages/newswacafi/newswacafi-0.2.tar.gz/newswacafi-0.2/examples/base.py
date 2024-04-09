from newswacafi.api import NewswacafiClient
from datetime import date

client = NewswacafiClient(
    api_key="6a07a7ee-***-b4504ebc0e68",
    api_secret="pbkdf2_sha256$6000***+g1R2MDOzS/QMoJstT6bWZTTVTcQlQ3cc="
)

news = client.get_news(
    start_date=date(2024, 1, 1), 
    end_date=date(2024, 2, 1), 
    country=['bf', 'ne'], 
    category=['politique'], 
    source=['lefaso.net', 'levenementniger.com'],
    query='elections'
)

print(news.data[0].title)