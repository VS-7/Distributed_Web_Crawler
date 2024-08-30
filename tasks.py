from celery import Celery
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from my_crawler.spiders.simple_spider import SimpleSpider

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task(bind=True)
def scrape_website(self, url):
    process = CrawlerProcess(get_project_settings())
    process.crawl(SimpleSpider, start_urls=[url])

    try:
        process.start()
    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)  # Tentar novamente em caso de falha
        logging.error(f'Erro ao iniciar o processo de scraping para a URL {url}: {e}')
