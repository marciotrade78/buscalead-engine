from bs4 import BeautifulSoup
import httpx


class WebScraperProvider:
    async def fetch_page_data(self, url: str) -> dict:
        try:
            async with httpx.AsyncClient(
                timeout=15,
                follow_redirects=True,
                headers={"User-Agent": "BuscaLeadBot/0.1 (+https://buscalead.local)"},
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            return {"status": "fetch_failed", "error": str(exc)}

        soup = self.parse_html(response.text)
        title = soup.title.string if soup.title and soup.title.string else None
        meta_description = soup.find("meta", attrs={"name": "description"})
        h1 = soup.find("h1")
        canonical = soup.find("link", attrs={"rel": "canonical"})

        return {
            "status": "fetched",
            "url": str(response.url),
            "title": title,
            "meta_description": meta_description.get("content") if meta_description else None,
            "h1": h1.get_text(" ", strip=True) if h1 else None,
            "canonical": canonical.get("href") if canonical else None,
            "html_size_bytes": len(response.content),
        }

    def parse_html(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "html.parser")
