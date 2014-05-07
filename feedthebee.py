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
    my_posts = feedparser.parse("http://www.drmaciver.com/feed/")

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
    if result.get('errors'):
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
