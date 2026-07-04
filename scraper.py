from feedgen.feed import FeedGenerator

fg = FeedGenerator()

fg.title("Prueba RSS")
fg.description("Feed de prueba")
fg.link(href="https://github.com")

entry = fg.add_entry()
entry.title("Hola Mundo")
entry.link(href="https://example.com")
entry.description("Esta es una prueba")

fg.rss_file("pogo_news_feed.xml")

print("RSS generado correctamente")
