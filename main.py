import logging

import aiohttp
import feedparser
import asyncio
from bs4 import BeautifulSoup
from bs4.element import Tag
from sqlalchemy.exc import IntegrityError

from database.connection import Session
from database.models import News

logger = logging.getLogger()
logging.basicConfig(filename='logs/parser.log', encoding='utf-8', level=logging.DEBUG)
INTERVAL = 0.6
feeds = []

session_db = Session()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def get_key_by_value(html_tags, value):
    for key, values in html_tags.items():
        if value in values:
            return key
    return None


async def fetchNewsFromUrl(loop, urls):
    cnt = 1
    while True:
        logger.info(f'Номер итерации: {cnt}')
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in urls:
                task = asyncio.create_task(
                    fetchNewsFromUrls(session, url)
                )
                tasks.append(task)
        cnt += 1
        await asyncio.sleep(120)



async def fetchNewsFromUrls(loop, url):
    while True:
        feed = feedparser.parse(url)
        logger.info(f'({url})- Пришло новостей: {len(feed.entries)}')
        async with aiohttp.ClientSession() as session:
            tasks = []
            for entry in feed.entries:
                is_new_news = session_db.query(News).filter(News.url == entry.link).first() is None
                if is_new_news:
                    task = asyncio.create_task(
                        get_page_data(session, entry, url, html_tags, html_attr)
                    )
                    tasks.append(task)
                    await asyncio.sleep(INTERVAL)
                else:
                    logger.info(f'{url} - Все новости обработаны!')
                    break
            await asyncio.gather(*tasks)
        await asyncio.sleep(120)

html_tags = {
    "div": [
        'https://ria.ru/export/rss2/archive/index.xml',
        'https://lenta.ru/rss',
        'https://www.kommersant.ru/RSS/news.xml',
        'https://news.rambler.ru/rss/world/',
        'https://news.rambler.ru/rss/community/',
        'https://news.rambler.ru/rss/incidents/',
        'https://news.rambler.ru/rss/tech/',
        'https://news.rambler.ru/rss/army/',
        'https://news.rambler.ru/rss/articles/',
        'https://news.rambler.ru/rss/games/'
    ],
    "article": ['https://tass.ru/rss/v2.xml'],

}
html_attr = {
    'https://ria.ru/export/rss2/archive/index.xml': {"class": "article__text"},
    'https://lenta.ru/rss': {"class": "topic-body__content"},
    'https://tass.ru/rss/v2.xml': {"class": ""},
    'https://www.kommersant.ru/RSS/news.xml': {"class": "article_text_wrapper"},
    'https://news.rambler.ru/rss/world/': {'data-news_media-desktop': "content_block"},
    'https://news.rambler.ru/rss/community/': {'data-news_media-desktop': "content_block"},
    'https://news.rambler.ru/rss/incidents/': {'data-news_media-desktop': "content_block"},
    'https://news.rambler.ru/rss/tech/': {'data-news_media-desktop': "content_block"},
    'https://news.rambler.ru/rss/army/': {'data-news_media-desktop': "content_block"},
    'https://news.rambler.ru/rss/articles/': {'data-news_media-desktop': "content_block"},
    'https://news.rambler.ru/rss/games/': {'data-news_media-desktop': "content_block"},
}


async def get_page_data(session, entry, main_url, html_tags, html_attr):
    async with session.get(url=entry.link) as response:
        response_text = await response.text()
        soup = BeautifulSoup(response_text, 'lxml')
        html_tag = get_key_by_value(html_tags, main_url)

        texts = soup.find_all(html_tag, html_attr[main_url])
        summary_text = ""
        for text in texts:
            summary_text += text.get_text().strip()
        new_record = News(
            text=summary_text,
            title=entry.title,
            url=entry.link,
        )

        try:
            session_db.add(new_record)
            session_db.commit()
            logger.info(f'Обработал страницу {entry.link}\n')
        except IntegrityError as e:
            session_db.rollback()
            logger.info(f'Ошибка: запись с URL {entry.link} уже существует в базе данных.')

logger.info('ЗАПУСК ПАРСЕРА')
loop = asyncio.get_event_loop()
loop.run_until_complete(fetchNewsFromUrl(loop, [
    'https://ria.ru/export/rss2/archive/index.xml',
    'https://lenta.ru/rss',
    'https://tass.ru/rss/v2.xml',
    'https://www.kommersant.ru/RSS/news.xml',
    'https://news.rambler.ru/rss/world/',
    'https://news.rambler.ru/rss/community/',
    'https://news.rambler.ru/rss/incidents/',
    'https://news.rambler.ru/rss/tech/',
    'https://news.rambler.ru/rss/army/',
    'https://news.rambler.ru/rss/articles/',
    'https://news.rambler.ru/rss/games/'
]))
