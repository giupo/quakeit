# -*- coding: utf-8 -*-

import twitter

import datetime
import re
import os
import json
import mimetypes

import tornado.web
import tornado.ioloop
import tornado.httpserver
from tornado.options import define, options, parse_command_line
from pkg_resources import Requirement, resource_filename

from sqlalchemy import create_engine, func
from sqlalchemy import Column, BIGINT, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

dburl = os.environ.get('DATABASE_URL',  'sqlite://')
engine = create_engine(dburl, echo=False)
Session = sessionmaker(bind=engine)

Base = declarative_base()

UPDATE_TIME = 1  # minute


def is_int(x):
    try:
        int(x)
        return True
    except ValueError:
        return False


class Quake(Base):
    __tablename__ = 'quake'
    id = Column(BIGINT, primary_key=True)
    zona = Column(String)
    ml = Column(Float)
    lat = Column(Float)
    lon = Column(Float)
    depth = Column(Float)
    text = Column(String)
    time = Column(DateTime)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return "<Quake(id='%s', text='%s')>" % (self.id, self.text)

Base.metadata.create_all(engine)

content_path = resource_filename(
    Requirement.parse("quakeit"), "public")


class DataFromTweet(object):
    pattern = re.compile("#terremoto\sML:([-+]?[0-9]*\.?[0-9]+)\s(\d+)-(\d+)-(\d+)\s(\d+):(\d+):(\d+\s)UTC\sLat=([-+]?[0-9]*\.?[0-9]+)\sLon=([-+]?[0-9]*\.?[0-9]+)\sProf=([-+]?[0-9]*\.?[0-9]+)Km\sZona=(.+)\.\s")  # noqa
    def __init__(self, tweet):
        self.id = tweet.id
        print tweet.text
        self.text = tweet.text
        match = DataFromTweet.pattern.match(self.text)
        if not match:
            self.id = 0
            return

        groups = match.groups()
        self.zona = groups[10]
        self.ml = float(groups[0])
        self.lat = float(groups[7])
        self.lon = float(groups[8])
        self.depth_km = float(groups[9])
        self.time = datetime.datetime(
            *[int(x) for x in groups[1:7]]
        )

    def to_dict(self):
        return {
            'id': self.id,
            'zona': unicode(self.zona),
            'ml': float(self.ml),
            'latitudine': float(self.lat),
            'longitudine': float(self.lon),
            'profondita': float(self.depth_km),
            'orario': self.time.isoformat(),
            'text': unicode(self.text)
        }

    def to_json(self):
        return json.dumps(self.to_dict())


def getData():
    CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
    CONSUMER_KEY = os.environ['CONSUMER_KEY']
    ACCESS_TOKEN_KEY = os.environ['ACCESS_TOKEN_KEY']
    ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']
    api = twitter.Api(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token_key=ACCESS_TOKEN_KEY,
        access_token_secret=ACCESS_TOKEN_SECRET
    )

    tweets = api.GetUserTimeline(screen_name="INGVterremoti", count=500)
    tweets = [t for t in tweets if t.text.startswith("#terremoto")]
    data = []
    for x in tweets:
        try:
            data_from_t = DataFromTweet(x)
            if data_from_t.id == 0:
                continue
            data.append(data_from_t)
        except Exception as e:
            print e
            pass

    data = [x for x in data
            if x.zona in ['Rieti', 'Ascoli Piceno', 'Perugia', 'Macerata']]
    data = [x for x in data
            if x.time > datetime.datetime(2016, 8, 21)]

    return data


def shouldUpdate(session):
    timestamp = session.query(func.max(Quake.time)).first()[0]
    if timestamp is None:
        return True
    else:
        now = datetime.datetime.now()
        return (now - timestamp).seconds >= UPDATE_TIME


def mergeWithDB(data, session):
    allids = [value[0] for value in session.query(Quake.id)]
    newids = [x.id for x in data]
    diff = list(set(newids) - set(allids))
    newdata = [x for x in data if x.id in diff]
    for datum in newdata:
        quake = Quake()
        quake.id = datum.id
        quake.text = datum.text
        quake.lat = datum.lat
        quake.lon = datum.lon
        quake.zona = datum.zona
        quake.ml = datum.ml
        quake.depth = datum.depth_km
        quake.time = datum.time
        session.add(quake)


# inserisco evento zero
session = Session()
try:
    session.query(Quake).filter_by(id=123).delete()

    class Tweet(object):
        pass
    tweet = Tweet()
    tweet.text = "#terremoto ML:6.0 2016-08-24 01:36:32 UTC " + \
                 "Lat=42.71 Lon=13.22 Prof=4Km Zona=Rieti."
    tweet.created_at = datetime.datetime(2016, 8, 24, 1, 36, 32)
    tweet.id = 1
    data = DataFromTweet(tweet)
    data.lat = 42.71
    data.lon = 13.22
    data.zona = "Rieti"
    data.ml = 6.0
    data.depth_km = 4
    data.time = tweet.created_at
    mergeWithDB([data], session)
    session.commit()
except Exception as e:
    print e
    session.rollback()
finally:
    session.close()


class DataController(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')

    def get(self, id=None):

        print "-------------------------", id, "-----------------"

        session = Session()
        try:
            if shouldUpdate(session):
                print "updating data"
                data = getData()
                mergeWithDB(data, session)
                session.commit()
                print "data updated"

            if id is None:
                data = [
                    x.to_dict()
                    for x in session.query(Quake).order_by(Quake.time).all()
                ]
                newdata = []
                for datum in data:
                    datum['time'] = datum['time'].isoformat()
                    newdata.append(datum)
                self.finish(json.dumps(newdata))
            else:
                if is_int(id):
                    data = session.query(Quake).get(int(id))
                    if data is None:
                        raise tornado.web.HTTPError(
                            status_code=404)

                    data = data.to_dict()
                    data['time'] = data['time'].isoformat()
                    self.finish(json.dumps(data))
                else:
                    data = [
                        x.to_dict()
                        for x in session.query(Quake).filter_by(zona=id).all()
                    ]
                    print data
                    newdata = []
                    for datum in data:
                        datum['time'] = datum['time'].isoformat()
                        newdata.append(datum)
                    self.finish(json.dumps(newdata))

        except Exception as e:
            print (e)
            session.rollback()
            raise tornado.web.HTTPError(
                status_code=500)
        finally:
            session.close()


class MainController(tornado.web.RequestHandler):
    def get(self, what="index.html"):
        if what is None or len(what) == 0:
            what = 'index.html'

        if what.endswith(".html") or "." not in what:
            what = "index.html"

        content_type = mimetypes.guess_type(what)
        self.set_header("Content-Type", content_type[0])

        try:
            with open(os.path.join(content_path, what)) as f:
                self.finish(f.read())
        except IOError:
            self.finish("404: Not Found")

routes = [
    (r'/data/(.*)', DataController),
    (r'/data', DataController),
    (r'/(.*)', MainController),
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
    port = int(os.environ.get('PORT', options.port))
    server.listen(port)
    tornado.ioloop.IOLoop.instance().start()


def main():
    startServer()

if __name__ == '__main__':
    startServer()
