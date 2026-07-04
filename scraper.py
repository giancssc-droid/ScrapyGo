from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import xml.etree.ElementTree as ET

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

    title = " ".join(title.split())

    items.append({
        "title": f"[{source}] {title}",
        "link": link,
        "date": datetime.now(timezone.utc)
    })


# =====================================================
# OFFICIAL POKEMON GO
# =====================================================

def pokemon_go_news():

    try:

        url = "https://pokemongo.com/es/news"

        r = requests.get(url, headers=HEADERS, timeout=30)

        soup = BeautifulSoup(r.text, "html.parser")

        seen = set()

        for a in soup.find_all("a", href=True):

            href = a["href"]

            if "/news/" not in href:
                continue

            title = a.get_text(" ", strip=True)

            if len(title) < 10:
                continue

            link = urljoin(url, href)

            if link in seen:
                continue

            seen.add(link)

            add_item(
                title,
                link,
                "Official"
            )

    except Exception as e:
        print("Official:", e)


# =====================================================
# GO HUB RSS
# =====================================================

def gohub_news():

    try:

        feed_url = (
            "https://pokemongohub.net/post/category/news/feed/"
        )

        r = requests.get(
            feed_url,
            headers=HEADERS,
            timeout=30
        )

        root = ET.fromstring(r.content)

        for item in root.findall(".//item"):

            title = item.findtext("title")
            link = item.findtext("link")

            if not title or not link:
                continue

            add_item(
                title,
                link,
                "GO Hub"
            )

    except Exception as e:
        print("GO Hub:", e)


# =====================================================
# LEEKDUCK EVENTS
# =====================================================

def leekduck_events():

    try:

        url = "https://leekduck.com/events/"

        r = requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )

        soup = BeautifulSoup(
            r.text,
            "html.parser"
        )

        seen = set()

        for a in soup.find_all("a", href=True):

            href = a.get("href", "")

            if "/events/" not in href:
                continue

            link = urljoin(url, href)

            if link in seen:
                continue

            seen.add(link)

            title = a.get_text(
                " ",
                strip=True
            )

            title = " ".join(title.split())

            if len(title) < 5:
                continue

            if title.lower() == "events":
                continue

            if "example event template" in title.lower():
                continue

            source = "LeekDuck Event"

            if "raid hour" in title.lower():
                source = "LeekDuck Raid Hour"

            elif "spotlight hour" in title.lower():
                source = "LeekDuck Spotlight"

            elif "mega raids" in title.lower():
                source = "LeekDuck Raid"

            elif "5-star raid" in title.lower():
                source = "LeekDuck Raid"

            elif "raid day" in title.lower():
                source = "LeekDuck Raid"

            elif "community day" in title.lower():
                source = "LeekDuck Community Day"

            # limpiar duplicados típicos

            replacements = [
                "Raid Battles Raid Battles ",
                "Raid Hour Raid Hour ",
                "Pokémon Spotlight Hour Pokémon Spotlight Hour ",
                "Community Day Community Day ",
                "Event Event ",
                "GO Pass GO Pass ",
                "GO Battle League GO Battle League ",
                "Max Mondays Max Mondays ",
                "Choose Your Path Choose Your Path ",
                "Pokémon GO Fest Pokémon GO Fest "
            ]

            for rep in replacements:
                title = title.replace(rep, "")

            add_item(
                title,
                link,
                source
            )

    except Exception as e:
        print("LeekDuck:", e)


# =====================================================
# RAID BOSSES
# =====================================================

def raid_bosses():

    add_item(
        "Current Raid Bosses",
        "https://leekduck.com/raid-bosses/",
        "LeekDuck Raid Bosses"
    )


# =====================================================
# RESEARCH
# =====================================================

def research_tasks():

    add_item(
        "Current Research Tasks",
        "https://leekduck.com/research/",
        "LeekDuck Research"
    )


# =====================================================
# RUN
# =====================================================

pokemon_go_news()
gohub_news()
leekduck_events()
raid_bosses()
research_tasks()

# eliminar duplicados

unique = {}

for item in items:
    unique[item["link"]] = item

items = list(unique.values())

# ordenar

items.sort(
    key=lambda x: x["date"],
    reverse=True
)

# limitar

items = items[:150]

# RSS

fg = FeedGenerator()

fg.title("Pokemon GO News & Events")
fg.description(
    "Official Pokemon GO + GO Hub + LeekDuck"
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

fg.rss_file(
    "pogo_news_feed.xml"
)

print(
    f"Feed generado con {len(items)} entradas"
)
