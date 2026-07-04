from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
import requests
import xml.etree.ElementTree as ET

FEEDS = [
    "https://pokemongo.com/en/feed/",
    "https://pokemongohub.net/feed/"
]

items = []


def parse_feed(feed_url):
    try:
        response = requests.get(
            feed_url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/137.0.0.0 Safari/537.36"
                )
            },
            timeout=30
        )

        root = ET.fromstring(response.content)

        for item in root.findall(".//item"):

            title = item.findtext("title", "")
            link = item.findtext("link", "")
            pub_date = item.findtext("pubDate")

            try:
                published = datetime.strptime(
                    pub_date,
                    "%a, %d %b %Y %H:%M:%S %z"
                )
            except:
                published = datetime.now(timezone.utc)

            items.append({
                "title": title,
                "link": link,
                "published": published
            })

    except Exception as e:
        print(f"Error leyendo {feed_url}: {e}")


for feed in FEEDS:
    parse_feed(feed)

unique = {}

for item in items:
    unique[item["link"]] = item

items = list(unique.values())

items.sort(
    key=lambda x: x["published"],
    reverse=True
)

fg = FeedGenerator()

fg.title("Pokemon GO Unified News Feed")
fg.link(href="https://github.com")
fg.description(
    "Pokemon GO Blog + Pokemon GO Hub"
)

for item in items:

    fe = fg.add_entry()

    fe.title(item["title"])
    fe.link(href=item["link"])
    fe.guid(item["link"])
    fe.pubDate(item["published"])

fg.rss_file("pogo_news_feed.xml")

print(f"Feed generado con {len(items)} artículos.")
