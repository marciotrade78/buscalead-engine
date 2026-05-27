from bs4 import BeautifulSoup


class WebScraperProvider:
    def parse_html(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "html.parser")
