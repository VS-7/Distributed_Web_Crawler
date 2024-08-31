import scrapy
import sqlite3

class SimpleSpider(scrapy.Spider):
    name = "simple_spider"
   # allowed_domains = ["g1.globo.com", "noticias.uol.com.br", "cnnbrasil.com.br"]

    custom_settings = {
        'ROBOTSTXT_OBEY': True,  # Respeitar o robots.txt
        'LOG_LEVEL': 'INFO'  # Configurar nível de log para informação
    }
    
    def __init__(self, *args, **kwargs):
        super(SimpleSpider, self).__init__(*args, **kwargs)

        # Conexão ao banco de dados SQLite
        try:
            self.conn = sqlite3.connect('database.db')
            self.cursor = self.conn.cursor()
            self.start_urls = self.get_seed_urls()  # Carrega as URLs do banco de dados
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS pages (
                    title TEXT,
                    url TEXT,
                    content TEXT
                )
            ''')
            self.logger.info('Conexão ao banco de dados SQLite estabelecida com sucesso.')
        except sqlite3.Error as e:
            self.logger.error(f'Erro ao conectar ao banco de dados SQLite: {e}')
            raise

    def get_seed_urls(self):
        self.cursor.execute("SELECT url FROM seeds")
        return [row[0] for row in self.cursor.fetchall()]

    def parse(self, response):
        try:
            page_title = response.css('title::text').get()
            page_url = response.url
            page_content = response.body.decode('utf-8')

            # Salvando dados no banco de dados
            self.save_to_db(page_title, page_url, page_content)

            self.logger.info(f'Successfully crawled: {page_url}')

            yield {
                'title': page_title,
                'url': page_url,
                'content': page_content
            }

            for next_page in response.css('a::attr(href)').getall():
                if next_page is not None:
                    yield response.follow(next_page, self.parse)

        except Exception as e:
            self.logger.error(f'Erro ao processar a resposta para a URL {response.url}: {e}')

    def save_to_db(self, title, url, content):
        try:
            self.cursor.execute("INSERT INTO pages (title, url, content) VALUES (?, ?, ?)", (title, url, content))
            self.conn.commit()
            self.logger.info(f'Dados salvos no banco de dados para a URL {url}.')
        except sqlite3.Error as e:
            self.logger.error(f'Erro ao salvar no banco de dados: {e}')

    def close(self, reason):
        try:
            self.conn.close()  # Fechar conexão ao banco de dados
            self.logger.info('Conexão ao banco de dados SQLite fechada.')
        except sqlite3.Error as e:
            self.logger.error(f'Erro ao fechar o banco de dados: {e}')
