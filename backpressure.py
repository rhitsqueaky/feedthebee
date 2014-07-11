"""
A script for encouraging you to be generally more on top of your beeminder
goals. Goals which have less than a week (configurable) before panic contribute
backpressure, which is then put into a "do less" goal.

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

import argparse
import hashlib
import requests
import json
from datetime import datetime
import math
import time


def all_goals(auth_token):
    result = json.loads(requests.get(
        "https://www.beeminder.com/api/v1/users/me/goals.json", params={
            "auth_token": auth_token
        }).text)

    if isinstance(result, dict) and result.get("errors"):
        raise ValueError(result["errors"])
    return result


def impending_goals(auth_token, max_days):
    for goal in all_goals(auth_token):
        if goal["goal_type"] != "hustler":
            continue
        losedate = datetime.utcfromtimestamp(goal["losedate"])
        now = datetime.utcnow()
        days_remaining = int(math.ceil(
            (losedate - now).total_seconds() / (24 * 60 * 60)))
        if days_remaining < max_days:
            yield goal["slug"], days_remaining


def apply_backpressure(auth_token, max_days, target_goal):
    date_string = datetime.now().strftime("%Y-%m-%d")
    timestamp = time.time()

    datapoints = []
    for goal, days in impending_goals(
        auth_token=auth_token, max_days=max_days
    ):
        if goal == target_goal:
            continue

        requestid = hashlib.sha1(date_string + ":" + goal).hexdigest()[:16]
        datapoint = {
            'requestid': requestid,
            'timestamp': timestamp,
            'value': 1,
            'comment': "Goal %s has %d days remaining" % (goal, days),
        }
        datapoints.append(datapoint)
    if datapoints:
        datapoints = json.dumps(datapoints)
        api_url = (
            "https://www.beeminder.com/api/v1/users/me/goals/%s/"
            "datapoints/create_all.json"
        ) % (
            target_goal,
        )

        response = requests.post(api_url, data={
            'datapoints': datapoints,
            'auth_token': auth_token
        })

        result = json.loads(response.text)
        if isinstance(result, dict) and result.get('errors'):
            raise ValueError([json.loads(e)["comment"] for e in result["errors"]])


def main():
    parser = argparse.ArgumentParser(
        description='Put word counts for a feed into beeminder'
    )
    parser.add_argument('--auth-token', type=str, required=True,
                        help='The API key to use for beeminder')
    parser.add_argument('--max-days', type=int, default=7,
                        help='Goals with fewer than this many days'
                        'remaining create backpressure')
    parser.add_argument('--target-goal', type=str, default='backpressure',
                        help='The beeminder goal to post to')
    args = parser.parse_args()

    apply_backpressure(**vars(args))

if __name__ == '__main__':
    main()
