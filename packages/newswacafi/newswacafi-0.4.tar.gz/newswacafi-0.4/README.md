# Newswacafi

## Description

NEWSwacafi est une initiative innovante destinée à fournir aux décideurs et analystes une compréhension approfondie des dynamiques au Sahel. En exploitant la puissance du web scraping et des analyses de données avancées, notre plateforme offre des insights précieux pour anticiper les tensions et conflits.

Cette librairie permet d'exploiter l'API de Newswacafi avec Python.

## Installation

```bash
pip install newswacafi
```

## Utilisation

```python
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
    source=['lefaso.net', 'levenementniger.com']
)

print(news.data[0].title)
```

## License

[MIT](https://choosealicense.com/licenses/mit/)
```