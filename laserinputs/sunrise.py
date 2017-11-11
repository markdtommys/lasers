import json
import urllib2

def performactions():
    """
    get the day length, sunrise and sunset times from sunrise-sunset.org
    current latlon is Cheltenham
    """
    url = 'https://api.sunrise-sunset.org/json?lat=51.83333&lng=-2.066667'
    try:
        getrequest = urllib2.urlopen(url)
    except:
        returnstring = 'unable to connect to sunrise-sunset.org'
    jsontext = json.loads(getrequest.read())
    sunrise = jsontext['results']['sunrise']
    sunset = jsontext['results']['sunset']
    daylength = jsontext['results']['day_length']
    returnstring = 'day length {} sunrise {} sunset {}'.format(daylength, sunrise, sunset)
    return returnstring


