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
            padding=ft.padding.symmetric(horizontal=5),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        controls= [
                            ft.Image(src='../assets/icons/logo_price.png', width=60),
                            ft.Text(value='Prices Finder', size=16)
                        ]
                        ),
                    
                    ft.ElevatedButton(
                        icon=ft.icons.ADD,
                        text="Ativar Crawler", 
                        on_click=self.on_option_click, 
                        width=300, 
                        height=40, 
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.with_opacity(0.1, ft.colors.BLACK), 
                            color=ft.colors.WHITE, 
                            shape=ft.RoundedRectangleBorder(radius=10)
                        )
                    ),
                    ft.ElevatedButton(
                        icon=ft.icons.BLOCK ,
                        text="Parar Crawler",  # Botão para parar o crawler
                        on_click=self.on_option_click, 
                        width=300, 
                        height=40, 
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.WHITE, 
                            color=ft.colors.BLACK, 
                            shape=ft.RoundedRectangleBorder(radius=10)
                        )
                    ),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        icon=ft.icons.DOWNLOAD,
                        text="Downloads", 
                        on_click=self.on_option_click, 
                        width=300, height=40, 
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.with_opacity(0.1, ft.colors.BLACK), 
                            color=ft.colors.WHITE, 
                            shape=ft.RoundedRectangleBorder(radius=10)
                        )
                    ),
                    ft.ElevatedButton(
                        icon=ft.icons.SETTINGS,
                        text="Settings", 
                        on_click=self.on_option_click, 
                        width=300, 
                        height=40, 
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.with_opacity(0.1, ft.colors.BLACK),
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

            # Conecta ao banco de dados e obtém as URLs
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT url FROM seeds")
            urls = [row[0] for row in cursor.fetchall()]
            conn.close()

            # Executa o script de scraping para cada URL
            from tasks import scrape_website
            for url in urls:
                scrape_website.delay(url)
            
            e.page.snack_bar = ft.SnackBar(
                                content=ft.Text("Crawler ativado com sucesso!"),
                                        bgcolor=ft.colors.GREEN_100,
                                        show_close_icon= True,
                                        close_icon_color=ft.colors.GREEN,
                                        padding=ft.padding.all(10),
                                        duration=5000,
                                        behavior=ft.SnackBarBehavior.FLOATING,
                                        margin=ft.margin.all(40),
                                        dismiss_direction=ft.DismissDirection.START_TO_END
                                )
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
                e.page.snack_bar = ft.SnackBar(
                                        content= ft.Text("Crawler parado com sucesso!"),
                                        bgcolor=ft.colors.GREY_100,
                                        show_close_icon= True,
                                        close_icon_color=ft.colors.GREY,
                                        padding=ft.padding.all(5),
                                        duration=5000,
                                        behavior=ft.SnackBarBehavior.FLOATING,
                                        margin=ft.margin.all(40),
                                        dismiss_direction=ft.DismissDirection.START_TO_END
                                        )
            else:
                e.page.snack_bar = ft.SnackBar(
                                        content=ft.Text("Nenhum Crawler está em execução."),
                                        bgcolor=ft.colors.GREY_100,
                                        show_close_icon= True,
                                        close_icon_color=ft.colors.GREY,
                                        padding=ft.padding.all(5),
                                        duration=5000,
                                        behavior=ft.SnackBarBehavior.FLOATING,
                                        margin=ft.margin.all(40),
                                        dismiss_direction=ft.DismissDirection.START_TO_END
                                        )
        except Exception as ex:
            e.page.snack_bar = ft.SnackBar(
                                    content=ft.Text(f"Erro ao parar o Crawler: {ex}"),
                                    bgcolor=ft.colors.RED_100,
                                    show_close_icon= True,
                                    close_icon_color=ft.colors.RED,
                                    padding=ft.padding.all(10),
                                    duration=5000,
                                    behavior=ft.SnackBarBehavior.FLOATING,
                                    margin=ft.margin.all(30),
                                    dismiss_direction=ft.DismissDirection.START_TO_END
                                )
        
        e.page.snack_bar.open = True
        e.page.update()

    def open_settings(self, e):
        def add_url(e):
            new_url = url_input.value
            if new_url:
                cursor.execute("INSERT INTO seeds (url) VALUES (?)", (new_url,))
                conn.commit()
                url_list.controls.append(url_item(new_url))  # Adiciona a URL com o botão de remoção
                e.page.update()

        def remove_url(e, url):
            cursor.execute("DELETE FROM seeds WHERE url=?", (url,))
            conn.commit()
            url_list.controls = [url_item(u) for u in get_urls()]  # Recria a lista de URLs
            e.page.update()

        def get_urls():
            cursor.execute("SELECT url FROM seeds")
            return [row[0] for row in cursor.fetchall()]

        def url_item(url):
            return ft.Row(
                controls=[
                    ft.Text(url),
                    ft.IconButton(
                        icon=ft.icons.DELETE,
                        on_click=lambda e: remove_url(e, url),  # Botão de remoção
                        icon_color=ft.colors.RED,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS seeds (url TEXT)')

        url_list = ft.Column(controls=[url_item(u) for u in get_urls()])
        url_input = ft.TextField(hint_text='Nova URL...',
                        hint_style=ft.TextStyle(size=15),
                        border_radius=ft.border_radius.all(10),
                        width=300,
                        height=40,
                        bgcolor=ft.colors.with_opacity(0.3, ft.colors.BLACK),
                        border_color=ft.colors.GREY_900,)
        
        add_button = ft.ElevatedButton(icon=ft.icons.ADD ,text="Adicionar URL", on_click=add_url, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), color=ft.colors.BLACK, bgcolor=ft.colors.WHITE))

        settings_dialog = ft.AlertDialog(
            title=ft.Text("Configurações de URLs"),
            shape=ft.RoundedRectangleBorder(radius=5),
            inset_padding=ft.padding.all(100),
            bgcolor=ft.colors.with_opacity(0.9, ft.colors.BLACK),
            content=ft.Column(
                scroll=True,
                controls=[
                    url_input,
                    add_button,
                    ft.Text(value='URLs cadastradas'),
                    url_list,
            ]),
        )
        e.page.dialog = settings_dialog
        settings_dialog.open = True
        e.page.update()
