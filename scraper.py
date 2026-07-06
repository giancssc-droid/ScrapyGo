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

            lower = title.lower()

            if "raid hour" in lower:
                source = "LeekDuck Raid Hour"

            elif "spotlight hour" in lower:
                source = "LeekDuck Spotlight"

            elif "community day" in lower:
                source = "LeekDuck Community Day"

            elif (
                "mega raids" in lower
                or "5-star raid" in lower
                or "raid day" in lower
            ):
                source = "LeekDuck Raid"

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
                source,
                datetime.now(timezone.utc),
                title
            )

    except Exception as e:
        print("LeekDuck:", e)


# =====================================================
# LEEKDUCK TWITTER / TELEGRAM
# =====================================================

def leekduck_twitter():

    try:

        feed = feedparser.parse(
            "https://rss-bridge.org/bridge01/?action=display&username=LeekDuckTwitter&bridge=TelegramBridge&format=Atom"
        )

        for entry in feed.entries[:25]:

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
# RUN
# =====================================================

pokemon_go_news()
gohub_events()
gohub_news()
leekduck_events()
leekduck_twitter()

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
