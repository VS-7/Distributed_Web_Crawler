import flet as ft
import sqlite3
import subprocess
import signal

class Sidebar(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.crawler_process = None  # Armazena o processo do Crawler

    def build(self):
        icons = ft.Container(
            padding=ft.padding.symmetric(vertical=10),
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        content=ft.Image(src='icons/001-instagram.png', height=15, color='white'),
                        url='https://www.instagram.com/vitor_sergiots/',
                    ),
                    ft.IconButton(
                        content=ft.Image(src='icons/002-linkedin.png', height=15, color='white'),
                        url='https://www.linkedin.com/company/66876059',
                    ),
                    ft.IconButton(
                        content=ft.Image(src='icons/003-github.png', height=15, color='white'),
                        url='https://github.com/VS-7',
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

        return ft.Container(
            padding=ft.padding.all(10),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(value="NEWS FINDER", size=20, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton(
                        icon=ft.icons.HOME_FILLED,
                        text="Home", 
                        on_click=self.on_option_click, 
                        width=300, 
                        height=80, 
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.WHITE10, 
                            color=ft.colors.WHITE, 
                            shape=ft.RoundedRectangleBorder(radius=10))
                    ),
                    ft.ElevatedButton(
                        text="Ativar Crawler", 
                        on_click=self.on_option_click, 
                        width=300, 
                        height=80, 
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.WHITE10, 
                            color=ft.colors.WHITE, 
                            shape=ft.RoundedRectangleBorder(radius=10)
                        )
                    ),
                    ft.ElevatedButton(
                        text="Parar Crawler",  # Botão para parar o crawler
                        on_click=self.on_option_click, 
                        width=300, 
                        height=80, 
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.RED, 
                            color=ft.colors.WHITE, 
                            shape=ft.RoundedRectangleBorder(radius=10)
                        )
                    ),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        icon=ft.icons.DOWNLOAD,
                        text="Downloads", 
                        on_click=self.on_option_click, 
                        width=300, height=80, 
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.WHITE10, 
                            color=ft.colors.WHITE, 
                            shape=ft.RoundedRectangleBorder(radius=10)
                        )
                    ),
                    ft.ElevatedButton(
                        icon=ft.icons.SETTINGS,
                        text="Settings", 
                        on_click=self.on_option_click, 
                        width=300, 
                        height=80, 
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.WHITE10, 
                            color=ft.colors.WHITE, 
                            shape=ft.RoundedRectangleBorder(radius=10)
                        )
                    ),
                    icons,
                ],
                spacing=10,
            ),
            width=200,
        )

    def on_option_click(self, e):
        if e.control.text == "Ativar Crawler":
            self.activate_crawler(e)
        elif e.control.text == "Parar Crawler":
            self.stop_crawler(e)  # Função para parar o crawler
        elif e.control.text == "Settings":
            self.open_settings(e)
        else:
            e.page.snack_bar = ft.SnackBar(ft.Text("Opção selecionada"))
            e.page.snack_bar.open = True
            e.page.update()

    def activate_crawler(self, e):
        try:
            # Inicia o Worker do Celery
            self.crawler_process = subprocess.Popen(['celery', '-A', 'tasks', 'worker', '--loglevel=info'])

            # Executa o script de scraping
            from tasks import scrape_website
            scrape_website.delay('https://g1.globo.com/mg/minas-gerais/')
            scrape_website.delay('https://noticias.uol.com.br/')
            scrape_website.delay('https://www.cnnbrasil.com.br/')
            
            e.page.snack_bar = ft.SnackBar(ft.Text("Crawler ativado com sucesso!"))
            e.page.snack_bar.open = True
            e.page.update()
        except Exception as ex:
            e.page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao ativar o Crawler: {ex}"))
            e.page.snack_bar.open = True
            e.page.update()

    def stop_crawler(self, e):
        try:
            if self.crawler_process:
                self.crawler_process.send_signal(signal.SIGTERM)  # Envia o sinal para parar o processo
                self.crawler_process = None
                e.page.snack_bar = ft.SnackBar(ft.Text("Crawler parado com sucesso!"))
            else:
                e.page.snack_bar = ft.SnackBar(ft.Text("Nenhum Crawler está em execução."))
        except Exception as ex:
            e.page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao parar o Crawler: {ex}"))
        
        e.page.snack_bar.open = True
        e.page.update()

    def open_settings(self, e):
        def add_url(e):
            new_url = url_input.value
            if new_url:
                cursor.execute("INSERT INTO seeds (url) VALUES (?)", (new_url,))
                conn.commit()
                url_list.controls.append(ft.Text(new_url))
                e.page.update()

        def remove_url(e, url):
            cursor.execute("DELETE FROM seeds WHERE url=?", (url,))
            conn.commit()
            url_list.controls = [ft.Text(u) for u in get_urls()]
            e.page.update()

        def get_urls():
            cursor.execute("SELECT url FROM seeds")
            return [row[0] for row in cursor.fetchall()]

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS seeds (url TEXT)')

        url_list = ft.Column(controls=[ft.Text(u) for u in get_urls()])
        url_input = ft.TextField(label="Nova URL")
        add_button = ft.ElevatedButton(text="Adicionar URL", on_click=add_url)

        settings_dialog = ft.AlertDialog(
            title=ft.Text("Configurações de URLs"),
            content=ft.Column(controls=[
                url_list,
                url_input,
                add_button,
            ]),
            actions=[
                ft.TextButton("Fechar", on_click=lambda e: e.control.close())
            ],
        )
        e.page.dialog = settings_dialog
        settings_dialog.open = True
        e.page.update()
