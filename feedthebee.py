"""
An extremely simple script for putting word counts from an RSS or similar feed
into a beeminder goal.

Copyright (C) 2014 David R. MacIver

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import print_function
import feedparser
import bs4
import time
import json
import hashlib
import requests
import argparse


class SyncError(Exception):
    def __init__(self, urls):
        self.urls = urls
        super(SyncError, self).__init__(
            "Unable to sync %d url%s" % (
                len(urls),
                "" if len(urls) == 1 else "s"
            )
        )


def sync_feed(user, goal, auth_token, feed):
    my_posts = feedparser.parse(feed)

    items = []
    for item in my_posts['items']:
        requestid = hashlib.sha1(item['id']).hexdigest()[:16]
        link = item['link']
        word_count = len(
            bs4.BeautifulSoup(item['content'][0]['value']).text.split()
        )
        timestamp = time.mktime(item.published_parsed)
        items.append({
            'requestid': requestid,
            'timestamp': timestamp,
            'value': word_count,
            'comment': link,
        })

    datapoints = json.dumps(items)

    api_url = (
        "https://www.beeminder.com/api/v1/users/%s/goals/%s/"
        "datapoints/create_all.json"
    ) % (
        user, goal
    )

    response = requests.post(api_url, data={
        'datapoints': datapoints,
        'auth_token': auth_token
    })

    result = json.loads(response.text)
    if isinstance(result, dict) and result.get('errors'):
        raise SyncError([json.loads(e)["comment"] for e in result["errors"]])


def main():
    parser = argparse.ArgumentParser(
        description='Put word counts for a feed into beeminder'
    )
    parser.add_argument('--auth-token', type=str, required=True,
                        help='The API key to use for beeminder')
    parser.add_argument('--feed', type=str, required=True,
                        help='The feed URL to fetch')
    parser.add_argument('--user', type=str, required=True,
                        help='The beeminder user to post to')
    parser.add_argument('--goal', type=str, required=True,
                        help='The beeminder goal to post to')
    args = parser.parse_args()

    try:
        sync_feed(**vars(args))
    except SyncError as e:
        print(str(e))
        for url in e.urls:
            print("  ", url)


if __name__ == '__main__':
    main()
