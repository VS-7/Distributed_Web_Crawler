from tasks import scrape_website

# Adiciona tarefas de scraping à fila
scrape_website.delay('https://g1.globo.com/mg/minas-gerais/')
scrape_website.delay('https://noticias.uol.com.br/')
scrape_website.delay('https://www.cnnbrasil.com.br/')
