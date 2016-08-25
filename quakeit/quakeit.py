# -*- coding: utf-8 -*-

import twitter

import datetime
import dateutil.parser
import pytz

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
engine = create_engine(dburl, echo=True)
Session = sessionmaker(bind=engine)

Base = declarative_base()

UPDATE_TIME = 1  # minute


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
    def __init__(self, tweet):
        self.id = tweet.id
        self.text = tweet.text
        data = tweet.text.split(' ')
        self.zona = data[8].replace('Zona=', '').replace('.', '')
        self.ml = float(data[1].replace('ML:', ''))
        self.lat = float(data[5].replace('Lat=', ''))
        self.lon = float(data[6].replace('Lon=', ''))
        self.depth_km = float(
            data[7].replace('Prof=', '').replace('Km', ''))
        self.time = dateutil.parser.parse(tweet.created_at)

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

    tweets = api.GetUserTimeline(screen_name="INGVterremoti", count=200)
    tweets = [t for t in tweets if t.text.startswith("#terremoto")]
    data = []
    for x in tweets:
        try:
            print x
            data.append(DataFromTweet(x))
        except Exception as e:
            print e
            pass

    data = [x for x in data
            if x.zona in ['Rieti', 'Ascoli Piceno', 'Perugia', 'Macerata']]
    data = [x for x in data
            if x.time > pytz.utc.localize(datetime.datetime(2016, 8, 21))]

    return data


def shouldUpdate(session):
    timestamp = session.query(func.max(Quake.time)).first()[0]
    if timestamp is None:
        return True
    else:
        now = datetime.datetime.now()
        return (now - timestamp.time).seconds >= UPDATE_TIME


def mergeWithDB(data, session):
    allids = [value for value in session.query(Quake.id).distinct()]
    newids = [x.id for x in data]
    diff = list(set(newids) - set(allids))
    newdata = [x for x in data if x.id in diff]

    for datum in newdata:
        print datum
        quake = Quake()
        quake.id = datum.id
        quake.text = datum.text
        quake.lat = datum.lat
        quake.lon = datum.lon
        quake.zona = datum.zona
        quake.ml = datum.ml
        quake.depth = datum.depth_km
        session.add(quake)


class DataController(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')

    def get(self, id=None):
        session = Session()
        try:
            if shouldUpdate(session):
                data = getData()
                print(data)
                mergeWithDB(data, session)
                session.commit()

            if id is None:
                data = [x.to_dict() for x in session.query(Quake).all()]
                self.finish(json.dumps(data))
            else:
                data = session.query(Quake).get(int(id))
                if data is None:
                    raise tornado.web.HTTPError(
                        status_code=404)
                self.finish(json.dumps(data.to_dict()))
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
