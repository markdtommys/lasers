import feedparser

def performactions():
    feed = feedparser.parse('http://open.live.bbc.co.uk/weather/feeds/en/2653261/observations.rss')
    observation = feed['entries'][0]['summary_detail']['value']
    source = feed['feed']['title']
    wxstring = source + ' ' + observation
    return wxstring
