import json

from tornado.httpclient import AsyncHTTPClient, HTTPRequest

from tornado import gen

from vizydrop.sdk.source import DataSource
from .filter import BlankFilter
from .schema import ApiExampleSchema
from toro import JoinableQueue, BoundedSemaphore


# how many concurrent fetches can we do?
FETCH_CONCURRENCY = 10
# our maximum request time (in seconds)
MAXIMUM_REQ_TIME = 30


class ApiExampleSource(DataSource):
    class Meta:
        identifier = "example"
        name = "Example"
        tags = ["example", ]
        description = "Just some example code"
        filter = BlankFilter

    class Schema(ApiExampleSchema):
        pass

    @classmethod
    @gen.coroutine
    def get_data(cls, account, source_filter, limit=100, skip=0):
        # set up our queue and semaphore
        queue = JoinableQueue()
        sem = BoundedSemaphore(FETCH_CONCURRENCY)
        done, working = set(), set()
        data = []

        # set up our coroutine to fetch our pages
        @gen.coroutine
        def fetch_url():
            current_url = yield queue.get()
            try:
                if current_url in working:
                    return
                page_no = working.__len__()
                # add the url we're fetching to our working set
                working.add(current_url)
                # and get it
                req = account.get_request(current_url)
                client = AsyncHTTPClient()
                response = yield client.fetch(req)
                # now we add our url to the set of done pages
                done.add(current_url)
                # and append the data we've received
                response_data = json.loads(response.body.decode('utf-8'))
                data.__add__(response_data.get('items', []))
                # check to see if there is a next page
                url = response_data.get('@odata.nextLink', None)
                if url is not None:
                    # and if there is one, stuff it in the queue
                    queue.put(url)
            finally:
                # ...and finally signal that we're done and release our semaphore
                queue.task_done()
                sem.release()

        # and set up the coroutine for our worker
        @gen.coroutine
        def worker():
            while True:
                yield sem.acquire()
                fetch_url()

        # the urls we will be fetching data from
        uris = ['http://some_paginated_odata_api/example/', 'http://some_paginated_odata_api/example2/']
        # fill our queue
        for uri in uris:
            queue.put(url)
        # start our queue worker
        worker()
        # wait until we're done
        yield queue.join(deadline=timedelta(seconds=MAXIMUM_REQ_TIME))

        # this helper function will "format" our data according to the schema we've specified above
        formatted = cls.format_data_to_schema(data)

        # and we're done
        return json.dumps(formatted)
