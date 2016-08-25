# -*- coding: utf-8 -*-

import twitter
import dateutil
import pandas
import datetime
import pytz
import pickle
import numpy
import os
import json

import tornado.web
import tornado.ioloop
import tornado.httpserver
from tornado.options import define, options, parse_command_line

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
    try:
        with open(OLD_DATA, 'rb') as f:
            old_values = pickle.load(f)
    except:
        old_values = {}
    
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
            old_values[k] = v

        with open(OLD_DATA, 'wb') as f:
            pickle.dump(old_values, f)
    except:
        with open(OLD_DATA, 'rb') as f:
            old_values = pickle.load(f)

    return old_values


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
    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')

    def get(self):
        try:
            encoded = {k.isoformat(): v for k, v in getData().iteritems()}
            self.finish(json.dumps(encoded))
        except Exception as e:
            self.finish(str(e))

routes = [
    (r'/', MainController)
]

settings = {
    "cookie_secret": os.environ['CONSUMER_SECRET'],
    "xsrf_cookies": False
}


application = tornado.web.Application(routes, **settings)

define("port", default=80, type=int, help="Listen port")
parse_command_line()


def startServer():
    server = tornado.httpserver.HTTPServer(application)
    server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


def main():
    startServer()

if __name__ == '__main__':
    startServer()
