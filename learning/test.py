import feedparser

url = "https://news.un.org/feed/subscribe/en/news/all/rss.xml"
feed = feedparser.parse(url)

print(type(feed.entries)) # What type? Type list - entries contains the list of articles from UN news
print(len(feed.entries))  # How many entries? 25 - the default number of articles shown in the feed
print(feed.entries[0].keys()) # What keys are available in the first entry? dict_keys(['title', 'title_detail', 'links', 'link', 'summary', 'summary_detail', 'id', 'guidislink', 'published', 'published_parsed', 'source'])