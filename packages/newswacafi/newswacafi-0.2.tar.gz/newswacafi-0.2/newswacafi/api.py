import requests
from datetime import date
from .response import NewsWacafiResponse, NewswacafiNews
from typing import List

class NewswacafiClient:
    def __init__(self, api_key, api_secret):
        self.base_url = 'https://api.newswacafi.online/'
        self.api_key = api_key
        self.api_secret = api_secret

    def get_news(self, start_date: date, end_date: date, source: List[str] = None, category: List[str] = None, country: List[str] = None, query: str = None) -> NewsWacafiResponse:
        '''
            Get news from the API
            :param start_date: date
            :param end_date: date
            :return: dict
        '''
        if not start_date or not end_date:
            raise ValueError('start_date and end_date are required')
        
        headers = {
            "Api-Key": self.api_key,
            "Api-Secret": self.api_secret
        }
        
        # format = DD-MM-YYYY
        start_date = start_date.strftime('%d-%m-%Y')
        end_date = end_date.strftime('%d-%m-%Y')

        req_url = f'{self.base_url}/news/?start_date={start_date}&end_date={end_date}'

        if source:
            source = ','.join(source)
            req_url += f'&source={source}'
        if category:
            category = ','.join(category)
            req_url += f'&category={category}'
        if country:
            country = ','.join(country)
            req_url += f'&country={country}'
        if query:
            req_url += f'&query={query}'

        response = requests.get(req_url, headers=headers)
        
        if response.ok:
            news_list = [NewswacafiNews(**news) for news in response.json()['data']]
            return NewsWacafiResponse(status=response.json()['status'], data=news_list)
        
        error = response.json()
        if 'detail' in error:
            raise ValueError(error['detail'])
        elif 'message' in error:
            raise ValueError(error['message'])
        else:
            raise ValueError('An error occured')
        