from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    )
}

items = []


def add_item(title, link, source):
    if not title or not link:
        return

    items.append({
        "title": f"[{source}] {title.strip()}",
        "link": link.strip(),
        "date": datetime.now(timezone.utc)
    })


# --------------------------------------------------
# Pokemon GO Official News
# --------------------------------------------------

def pokemon_go_news():
    try:
        url = "https://pokemongo.com/es/news"

        r = requests.get(url, headers=HEADERS, timeout=30)

        soup = BeautifulSoup(r.text, "html.parser")

        links = soup.find_all("a", href=True)

        seen = set()

        for a in links:

            href = a.get("href")

            if "/post/" not in href and "/news/" not in href:
                continue

            full_url = urljoin(url, href)

            title = a.get_text(" ", strip=True)

            if len(title) < 5:
                continue

            if full_url in seen:
                continue

            seen.add(full_url)

            add_item(title, full_url, "Official")

    except Exception as e:
        print("Pokemon GO:", e)


# --------------------------------------------------
# Pokemon GO Hub
# --------------------------------------------------

def pogo_hub_news():
    try:
        url = "https://pokemongohub.net/post/category/news/"

        r = requests.get(url, headers=HEADERS, timeout=30)

        soup = BeautifulSoup(r.text, "html.parser")

        articles = soup.find_all("article")

        for article in articles:

            a = article.find("a", href=True)

            if not a:
                continue

            title = a.get_text(" ", strip=True)

            if len(title) < 5:
                continue

            add_item(
                title,
                a["href"],
                "GO Hub"
            )

    except Exception as e:
        print("GO Hub:", e)


# --------------------------------------------------
# LeekDuck Events
# --------------------------------------------------

def leekduck_events():
    try:
        url = "https://leekduck.com/events/"

        r = requests.get(url, headers=HEADERS, timeout=30)

        soup = BeautifulSoup(r.text, "html.parser")

        links = soup.find_all("a", href=True)

        seen = set()

        for a in links:

            href = a["href"]

            if "/events/" not in href:
                continue

            title = a.get_text(" ", strip=True)

            if len(title) < 3:
                continue

            full_url = urljoin(url, href)

            if full_url in seen:
                continue

            seen.add(full_url)

            add_item(title, full_url, "Events")

    except Exception as e:
        print("LeekDuck Events:", e)


# --------------------------------------------------
# LeekDuck Raid Bosses
# --------------------------------------------------

def leekduck_raids():
    add_item(
        "Current Raid Bosses",
        "https://leekduck.com/raid-bosses/",
        "Raids"
    )


# --------------------------------------------------
# LeekDuck Research
# --------------------------------------------------

def leekduck_research():
    add_item(
        "Current Research Tasks",
        "https://leekduck.com/research/",
        "Research"
    )


pokemon_go_news()
pogo_hub_news()
leekduck_events()
leekduck_raids()
leekduck_research()

# Eliminar duplicados

unique = {}

for item in items:
    unique[item["link"]] = item

items = list(unique.values())

# Ordenar

items.sort(
    key=lambda x: x["date"],
    reverse=True
)

# Limitar

items = items[:100]

# RSS

fg = FeedGenerator()

fg.title("Pokemon GO Unified Feed")
fg.description(
    "Pokemon GO + GO Hub + LeekDuck"
)

fg.link(
    href="https://giancssc-droid.github.io/ScrapyGo/"
)

for item in items:

    fe = fg.add_entry()

    fe.title(item["title"])
    fe.link(href=item["link"])
    fe.guid(item["link"])
    fe.pubDate(item["date"])

fg.rss_file("pogo_news_feed.xml")

print(f"Feed generado con {len(items)} entradas")
