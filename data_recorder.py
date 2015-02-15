import urllib2
import urlparse
import time
import datetime


class BearwalkDataRecorder(object):
    def __init__(self, file):
        self.url = urlparse.ParseResult(scheme='http',
                                        netloc='bearwalk.berkeley.edu',
                                        path='/map/student',
                                        params='',
                                        query='',
                                        fragment='').geturl()
        self.request = urllib2.Request(self.url, '')
        self.file = file

    def get_response(self):
        print 'requesting'
        response = urllib2.urlopen(self.request)
        return json.loads(response.read())

    def record(self):
        with open(self.file, 'a') as f:
            while True:
                data = self.get_response()
                string = json.dumps({str(datetime.datetime.now()): data})
                f.write('{}\n'.format(string))

                time.sleep(5)


