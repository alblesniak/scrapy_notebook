BOT_NAME = 'scrapy_app'

SPIDER_MODULES = ['scrapy_app.spiders']
NEWSPIDER_MODULE = 'scrapy_app.spiders'

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36'

ROBOTSTXT_OBEY = False

SPIDER_MIDDLEWARES = {
   'scrapy_app.middlewares.ScrapyAppSpiderMiddleware': 543,
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy_app.middlewares.ScrapyAppDownloaderMiddleware': 543,
    'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
}

ITEM_PIPELINES = {
    'scrapy_app.pipelines.FullfillDataPipeline': 100,
    'scrapy_app.pipelines.ShortestPipeline': 200,
    'scrapy_app.pipelines.DuplicatesPipeline': 300,
    'scrapy_app.pipelines.Save2dbPipeline': 400,
}

CONNECTION_STRING = 'sqlite:///scrapy_weeklies.db'

ROTATING_PROXY_LIST = [
    '195.91.148.184:8080',
    '139.255.128.244:8080',
    '124.107.185.189:3128',
    '189.14.193.242:53281',
    '121.1.141.106:80',
    '125.26.7.124:61642',
    '191.101.39.29:80',
    '192.109.165.35:80',
    '89.187.177.99:80',
    '45.94.157.65:80',
    '89.187.177.94:80',
    '80.255.91.38:46185',
    '46.173.105.151:41258',
    '62.23.15.92:3128'
]
