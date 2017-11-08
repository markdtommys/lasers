import feedparser

def shorten_text(longstring):
    """
    take out uneeded words
    """
    wordstoremove = ['Temperature', 'Wind Direction', 'Wind Speed', 'Humidity', 'Pressure', 'Visibility', ':', ',']
    for word in wordstoremove:
        longstring = longstring.replace(word, '')
    return longstring

def performactions():
    feed = feedparser.parse('http://open.live.bbc.co.uk/weather/feeds/en/2653261/observations.rss')
    observation = feed['entries'][0]['summary_detail']['value']
    source = feed['feed']['title']
    wxsummary = shorten_text(observation)
    wxstring = 'BBC Weather' + ' ' + wxsummary
    return wxstring
