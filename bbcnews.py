import feedparser
import sys

entry = 0
if len(sys.argv) > 1 :
    entry = int(sys.argv[1])

d = feedparser.parse('http://feeds.bbci.co.uk/news/rss.xml?edition=uk#')
print d.entries[entry].title

print d.entries[entry].keys()

print d.entries[entry].published
