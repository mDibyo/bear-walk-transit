import os
os.environ['http_proxy'] = ''

import urllib2
import urlparse
import time
import datetime
import json
from pymongo import MongoClient


class BeartransitDataRecorder(object):
    def __init__(self, file):
        self.url = urlparse.ParseResult(scheme='http',
                                        netloc='bearwalk.berkeley.edu',
                                        path='/map/student',
                                        params='',
                                        query='',
                                        fragment='').geturl()
        self.url = urlparse.ParseResult(scheme='http',
                                        netloc='bearwalk.berkeley.edu',
                                        path='/bustracking/api/v1/positions',
                                        params='',
                                        query='',
                                        fragment='').geturl()
        self.request = urllib2.Request(self.url, '')
        self.file = file

    def get_response(self):
        try:
            print 'requesting'
            response = urllib2.urlopen(self.url)
            return json.loads(response.read())
        except (urllib2.URLError, urllib2.HTTPError) as e:
            print 'request failed: {}'.format(e)
        except Exception as e:
            print e

    def record(self):
        with open(self.file, 'a') as f:
            while True:
                data = self.get_response()
                string = json.dumps({str(datetime.datetime.now()): data})
                f.write('{}\n$$$\n'.format(string))

                time.sleep(5)


class BeartransitDatabaseDataRecorder(BeartransitDataRecorder):
    DATABASE_PORT = 27017
    DATABASE_URL = 'localhost'

    DATABASE_NAME = 'bear_transit'
    COLLECTION_NAME = 'api_call'

    def __init__(self):
        super(BeartransitDatabaseDataRecorder, self).__init__("")

        self.client = MongoClient(self.DATABASE_URL, self.DATABASE_PORT)
        self.db = self.client[self.DATABASE_NAME]
        self.db_collection = self.db[self.COLLECTION_NAME]

    def record(self):
        while True:
            data = self.get_response()
            self.db_collection.insert({
                "timestamp": time.time(),
                "data": data
            })

            time.sleep(5)


if __name__ == '__main__':
    from argparse import ArgumentParser

    description = 'Record results of API calls to Bear Transit'
    parser = ArgumentParser(description=description)
    parser.add_argument('--url', '-u',
                        default=BeartransitDatabaseDataRecorder.DATABASE_URL)
    parser.add_argument('--port', '-p', type=int,
                        default=BeartransitDatabaseDataRecorder.DATABASE_PORT)
    parser.add_argument('--database', '-d',
                        default=BeartransitDatabaseDataRecorder.DATABASE_NAME)
    parser.add_argument('--collection', '-c',
                        default=BeartransitDatabaseDataRecorder.COLLECTION_NAME)
    args = parser.parse_args()

    BeartransitDatabaseDataRecorder.DATABASE_URL = args.url
    BeartransitDatabaseDataRecorder.DATABASE_PORT = args.port
    BeartransitDatabaseDataRecorder.DATABASE_NAME = args.database
    BeartransitDatabaseDataRecorder.COLLECTION_NAME = args.collection

    recorder = BeartransitDatabaseDataRecorder()
    recorder.record()
