from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import xml.etree.ElementTree as ET
import feedparser

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    )
}

items = []


def add_item(title, link, source, date=None, description=""):

    if not title or not link:
        return

    if date is None:
        date = datetime.now(timezone.utc)

    title = " ".join(title.split())

    items.append({
        "title": f"[{source}] {title}",
        "link": link,
        "date": date,
        "description": description
    })


# =====================================================
# OFFICIAL POKEMON GO
# =====================================================

def pokemon_go_news():

    try:

        url = "https://pokemongo.com/es/news"

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
        max_articles = 10

        for a in soup.find_all("a", href=True):

            href = a.get("href", "")

            if "/news/" not in href:
                continue

            if href.endswith("/news"):
                continue

            link = urljoin(url, href)

            if link in seen:
                continue

            title = a.get_text(
                " ",
                strip=True
            )

            if len(title) < 5:
                continue

            seen.add(link)

            if len(seen) > max_articles:
                break

            description = (
                f"Artículo oficial de Pokémon GO: {title}"
            )

            add_item(
                title,
                link,
                "Official",
                datetime.now(timezone.utc),
                description
            )

    except Exception as e:
        print("Official:", e)


# =====================================================
# GO HUB EVENTS
# =====================================================

def gohub_events():

    try:

        feed_url = (
            "https://pokemongohub.net/post/category/event/feed/"
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
            pub_date = item.findtext("pubDate")
            description = item.findtext("description") or ""

            if not title or not link:
                continue

            try:
                published = parsedate_to_datetime(pub_date)
            except:
                published = datetime.now(timezone.utc)

            add_item(
                title,
                link,
                "GO Hub Events",
                published,
                description[:1200]
            )

    except Exception as e:
        print("GO Hub Events:", e)


# =====================================================
# GO HUB NEWS
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
            pub_date = item.findtext("pubDate")
            description = item.findtext("description") or ""

            if not title or not link:
                continue

            try:
                published = parsedate_to_datetime(pub_date)
            except:
                published = datetime.now(timezone.utc)

            add_item(
                title,
                link,
                "GO Hub News",
                published,
                description[:1200]
            )

    except Exception as e:
        print("GO Hub News:", e)


# =====================================================
# LEEKDUCK TWITTER / TELEGRAM
# =====================================================

def leekduck_twitter():

    try:

        feed = feedparser.parse(
            "https://rss-bridge.org/bridge01/?action=display&username=LeekDuckTwitter&bridge=TelegramBridge&format=Atom"
        )

        for entry in feed.entries[:10]:

            title = getattr(entry, "title", "")
            link = getattr(entry, "link", "")

            if not title or not link:
                continue

            try:
                published = parsedate_to_datetime(
                    entry.published
                )
            except:
                published = datetime.now(timezone.utc)

            add_item(
                title,
                link,
                "LeekDuckTwitter",
                published,
                title
            )

    except Exception as e:
        print("LeekDuckTwitter:", e)


# =====================================================
# CURRENT GAME DATA
# =====================================================

def raid_bosses():

    add_item(
        "Current Raid Bosses",
        "https://leekduck.com/raid-bosses/",
        "LeekDuck Raid Bosses",
        datetime.now(timezone.utc),
        "Lista actual de jefes de incursión."
    )


def research_tasks():

    add_item(
        "Current Research Tasks",
        "https://leekduck.com/research/",
        "LeekDuck Research",
        datetime.now(timezone.utc),
        "Lista actual de investigaciones."
    )


def spotlight_raid_hours():

    add_item(
        "Spotlight & Raid Hours",
        "https://pokemongohub.net/post/guide/spotlight-raid-hours/",
        "GO Hub Schedule",
        datetime.now(timezone.utc),
        "Calendario actual de Raid Hours y Spotlight Hours."
    )


# =====================================================
# RUN
# =====================================================

pokemon_go_news()
gohub_events()
gohub_news()
leekduck_twitter()

raid_bosses()
research_tasks()
spotlight_raid_hours()

# =====================================================
# REMOVE DUPLICATES
# =====================================================

unique = {}

for item in items:
    unique[item["link"]] = item

items = list(unique.values())

# =====================================================
# SORT
# =====================================================

items.sort(
    key=lambda x: x["date"],
    reverse=True
)

items = items[:50]

# =====================================================
# GENERATE FEED
# =====================================================

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
    fe.description(item["description"])

fg.rss_file("pogo_news_feed.xml")

print(
    f"Feed generado con {len(items)} entradas"
)
