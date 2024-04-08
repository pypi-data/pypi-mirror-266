from setuptools import setup, find_packages

setup(
    name='RabbitSpider',
    version='1.0.0',
    author_email='2395396520@qq.com',
    packages=['RabbitSpider', 'RabbitSpider.core', 'RabbitSpider.http', 'RabbitSpider.utils'],
    python_requires='>=3.8',
    install_requires=[
        'aio-pika~=9.4.1',
        'aiohttp~=3.9.3',
        'pydantic~=2.6.4',
        'chardet~=5.2.0',
        'parsel~=1.9.0',
        'w3lib~=2.1.2',
        'requests~=2.31.0',
        'redis~=5.0.3',
        'uvicorn~=0.29.0',
        'starlette~=0.37.2',
        'fastapi~=0.110.1',
        'SQLAlchemy~=2.0.29',
        'loguru~=0.7.2',
    ]
)


