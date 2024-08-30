import flet as ft
from components.news_finder import NewsFinderApp

if __name__ == "__main__":
    app = NewsFinderApp()
    ft.app(target=app.main)
