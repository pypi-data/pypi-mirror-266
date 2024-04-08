import json
from typing import Any, Dict

from .spider_auth import spider_auth
from .settings import *

class ScrapyPublish:
    def __init__(self, **kwargs):
        # scrapy + spider context
        self.scrapy:Any = kwargs.get('scrapy')
        self.ctx:Any = kwargs.get('ctx')

        # custom settings
        self.source_domain = kwargs.get('source_domain')
        self.target_id_key = kwargs.get('target_id_key', 'post_id')
        self.db_command = kwargs.get('db_command')
        self.api_action = kwargs.get('api_action', 'add')

        # auth token
        self.token = spider_auth()

    def publish(self, items):
        for item in items:
            yield self.publish_one(item)

    def publish_one(self, item):
        api_url = f'{SPIDER_API_URL}/api/python/post/{self.api_action}'
        token = self.token
        ctx = self.ctx
        ctx.logger.info('Current data id is %s' % item.get('article_id'))
        # post json to api
        headers = {'Content-Type': 'application/json', 'Authorization': f'bearer {token}'}
        json_body = json.dumps({
            'title': item.get('title'),
            'content': item.get('content'),
            'cover': item.get('cover_pid'),
            'source_domain': self.source_domain,
            'url': item.get('url'),
        })

        # self.logger.info('Current record is %s' % record)

        yield self.scrapy.Request(
            url=api_url,
            method='POST',
            body=json_body,
            headers=headers,
            meta={'record': item},
            callback=self.parse_api_response
        )

    def parse_api_response(self, response):
        record = response.meta['record']
        status = response.status
        text = response.text
        ctx = self.ctx
        target_id_key = self.target_id_key
        target_id_value = record.get(target_id_key)
        db_command = self.db_command

        if status == 200:
            ctx.logger.info('Data id %s is inserted' % record.get('article_id'))
            payload = {
                'insert2db_response': None,
                'is_crawled': True,
            }

        else:
            ctx.logger.error('Data id %s is failed' % record.get('article_id'))
            payload = {
                'insert2db_response': {'status': status, 'body': text},
            }

        payload[target_id_key] = target_id_value

        yield {
            'command': db_command,
            'payload': payload
        }
