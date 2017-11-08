import feedparser
import sys

entry = 0
if len(sys.argv) > 1 :
    entry = int(sys.argv[1])

d = feedparser.parse('http://open.live.bbc.co.uk/weather/feeds/en/2653261/observations.rss')
print "Title : " + d.entries[entry].title

print "Keys : " 

print d.entries[entry].keys()

print "Pulished : " + d.entries[entry].published

print d.entries[entry]
