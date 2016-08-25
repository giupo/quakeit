# -*- coding: utf-8 -*-

import twitter
import dateutil
import pandas
import datetime
import pytz
import matplotlib
import pickle
import numpy
import os

import tornado.web
import tornado.ioloop
import tornado.httpserver


OLD_DATA = "old_data"

CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
CONSUMER_KEY = os.environ['CONSUMER_KEY']
ACCESS_TOKEN_KEY = os.environ['ACCESS_TOKEN_KEY']
ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']


def getData():
    class DataFromTweet(object):
        def __init__(self, tweet):
            data = tweet.text.split(' ')
            self.zona = data[8].replace('Zona=', '').replace('.', '')
            if self.zona not in ['Perugia', 'Rieti',
                                 'Ascoli Piceno', 'Macerata']:
                self.ml = 0
                return
            self.ml = float(data[1].replace('ML:', ''))
            self.lat = float(data[5].replace('Lat=', ''))
            self.lon = float(data[6].replace('Lon=', ''))
            self.depth_km = float(
                data[7].replace('Prof=', '').replace('Km', ''))
            self.zona = data[8].replace('Zona=', '').replace('.', '')
            self.time = dateutil.parser.parse(tweet.created_at)

    with open(OLD_DATA, 'rb') as f:
        values = pickle.load(f)

    try:
        api = twitter.Api(consumer_key=CONSUMER_KEY,
                          consumer_secret=CONSUMER_SECRET,
                          access_token_key=ACCESS_TOKEN_KEY,
                          access_token_secret=ACCESS_TOKEN_SECRET)

        tweets = api.GetUserTimeline(screen_name="INGVterremoti", count=200)
        tweets = [t for t in tweets if t.text.startswith("#terremoto")]
        data = [DataFromTweet(x) for x in tweets]
        data = [x for x in data if x.ml != 0]
        data = [x for x in data
                if x.time > pytz.utc.localize(datetime.datetime(2016, 8, 21))]

        values = [x.ml for x in data]
        values.append(numpy.nan)
        values.insert(0, numpy.nan)
        time = [x.time for x in data]
        time.insert(0, time[0] + datetime.timedelta(hours=1))
        time.append(time[-1] - datetime.timedelta(hours=1))
        new_values = dict(zip(time, values))
        for k, v in new_values.iteritems():
            values[k] = v

        with open(OLD_DATA, 'wb') as f:
            pickle.dump(values, f)
    except:
        with open(OLD_DATA, 'rb') as f:
            values = pickle.load(f)

    return values


def generateImage():
    data = getData()
    print data
    series = pandas.Series(data=data.values(), index=data.keys())
    title = "Intensita' #terremoto Italia Centrale " + \
            "(fonte @INGVterremoti)"
    plot = series.plot(grid=True, title=title)
    fig = plot.get_figure()
    fig.savefig('asdf.png')


class MainController(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello world")
        self.finish()

routes = [
    (r'/', MainController)
]

settings = {
    "cookie_secret": os.environ['CONSUMER_SECRET'],
    "xsrf_cookies": False
}


application = tornado.web.Application(routes, **settings)
port = 80


def startServer():
    server = tornado.httpserver.HTTPServer(application)
    server.listen(port)
    tornado.ioloop.IOLoop.instance().start()


def main():
    startServer()

if __name__ == '__main__':
    startServer()
