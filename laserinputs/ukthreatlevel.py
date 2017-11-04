import feedparser

def performactions():
    feed = feedparser.parse('https://www.mi5.gov.uk/UKThreatLevel/UKThreatLevel.xml')
    threatlevel = feed['entries'][0]['title']
    return threatlevel
