import flet as ft
import sqlite3
from components.sidebar import Sidebar

class NewsFinderApp:
    def __init__(self):
        self.news_list = None
        self.sidebar = Sidebar()

    def search_news(self, query):
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        query = f"SELECT title, url, content FROM pages WHERE title LIKE '%{query}%'"
        cursor.execute(query)
        news = cursor.fetchall()

        connection.close()
        return news

    def get_news_details(self, title):
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        query = f"SELECT title, url, content FROM pages WHERE title = ?"
        cursor.execute(query, (title,))
        news = cursor.fetchone()

        connection.close()
        return news

    def news_container(self, news, on_click):
        return ft.Container(
            padding=ft.padding.all(10),
            margin=ft.margin.only(bottom=10),
            bgcolor=ft.colors.with_opacity(0.2, ft.colors.BLACK),
            border_radius=ft.border_radius.all(10),
            content=ft.Column(
                controls=[
                    ft.Text(value=news[0], size=20, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        controls=[
                            ft.TextButton(
                                text="Acessar Página Web",
                                on_click=lambda e: e.page.launch_url(news[1]),
                                style=ft.ButtonStyle(bgcolor=ft.colors.WHITE, color=ft.colors.BLACK, shape=ft.RoundedRectangleBorder(radius=10))
                            ),
                            ft.TextButton(
                                text="Ver Detalhes",
                                on_click=lambda e: on_click(e.page, news[0]),
                                style=ft.ButtonStyle(color=ft.colors.WHITE),
                                
                            )
                        ]
                    )
                ]
            )
        )

    def show_news_details(self, page, title):
        news = self.get_news_details(title)
        if news:
            news_details = ft.Container(
                padding=ft.padding.all(20),
                border_radius=ft.border_radius.all(10),
                content=ft.Column(
                    controls=[
                        ft.Text(value=news[0], size=24, weight=ft.FontWeight.BOLD),
                        ft.Text(value=news[1], size=12, color=ft.colors.BLUE),
                        ft.Text(value="Conteúdo da Página:", size=14, weight=ft.FontWeight.BOLD),
                        ft.Markdown(value=news[2], selectable=True),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=500,
                height=700,
            )
            modal = ft.AlertDialog(
                bgcolor=ft.colors.BLACK87,
                shape=ft.RoundedRectangleBorder(radius=5),
                title=ft.Text("Detalhes da Notícia"),
                content=news_details,
                actions_alignment=ft.MainAxisAlignment.END,
                on_dismiss=lambda e: page.update()
            )
            page.dialog = modal
            modal.open = True
            page.update()

    def search(self, e):
        query = e.control.value
        news = self.search_news(query)
        if not news:
            self.news_list.controls = [ft.Text("Nenhuma notícia encontrada.")]
        else:
            self.news_list.controls = [self.news_container(n, self.show_news_details) for n in news]
        self.news_list.update()

    def main(self, page: ft.Page):
        page.padding = 0
        page.theme_mode = ft.ThemeMode.DARK
        
        page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary='#192233',
                on_primary='#fffff',
                background='#0d121c'
                
            )
        )

        '''banner=ft.Row(
            controls= [
                ft.Image(src='../assets/icons/banner.png', width=600, height=300),
                ft.Container(
                    width=400,
                    height=300,
                    bgcolor=ft.colors.with_opacity(0.3, ft.colors.BLACK),
                    margin=ft.margin.only(left=-40),
                    content=ft.Column(
                        controls=[
                            ft.Text(value="Documentação se encontra no Github")
                        ]
                    )
                )
            ]
        )
        '''
        searchbar = ft.Container(
            padding=ft.padding.only(top=20),
            content= ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls= [
                     ft.TextField(
                        prefix_icon=ft.icons.SEARCH,
                        hint_text='Digite o título da notícia...',
                        hint_style=ft.TextStyle(size=15, color=ft.colors.WHITE),
                        on_submit=self.search,
                        border_radius=ft.border_radius.all(15),
                        width=300,
                        height=40,
                        bgcolor=ft.colors.with_opacity(0.3, ft.colors.BLACK),
                        border_color=ft.colors.with_opacity(0.3, ft.colors.BLACK),
                    ),
                ]
            ),
        )

        self.news_list = ft.ListView(
            expand=True,
            controls=[],
        )

        layout = ft.Container(
            padding=ft.padding.only(top=20, left=10, right=20, bottom=20),
            gradient=ft.LinearGradient(
                        begin=ft.alignment.top_left,
                        end=ft.alignment.bottom_right,
                        colors=[ft.colors.PRIMARY, ft.colors.BACKGROUND]
                    ),
            
            expand=True,
            content= ft.Row(
                controls=[
                    self.sidebar,  
                    ft.Column(
                        expand=True,
                        controls=[
                            searchbar,
                            self.news_list,
                         ]
                    ),
                ]
            ),
        )

        page.add(layout)
