"""
Integration between todoist and beeminder. Every overdue task will generate a
data point in a beeminder goal each day it's overdue.

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

import requests
import json
from datetime import datetime
from time import time
import hashlib
import argparse
import beeminder


def fetch_overdue_tasks(todoist_auth_token):
    return [
        t
        for d in json.loads(
            requests.get("https://api.todoist.com/API/query", params={
                'token': todoist_auth_token,
                'queries': '["overdue"]'
            }).text)
        for t in d['data']
    ]


def import_overdue_tasks(
    todoist_auth_token, beeminder_auth_token, target_goal
):
    beeminder_goal = json.loads(
        requests.get(
            "https://www.beeminder.com/api/v1/users/me/goals/%s.json" % (
                target_goal,), params={
                    "auth_token": beeminder_auth_token
                }
        ).text
    )

    now = time()
    today = datetime.now().strftime("%Y-%m-%d")
    tasks = fetch_overdue_tasks(todoist_auth_token)
    if tasks:
        datapoints = []
        for task in tasks:
            dp = {
                'value': 1,
                'comment': task['content'],
                'timestamp': now,
                'request_id': hashlib.sha1(':'.join((
                    today,
                    beeminder_goal['id'],
                    str(task['id']),
                ))).hexdigest()[:16]
            }
            datapoints.append(dp)
        beeminder.submit_datapoints(
            datapoints=datapoints,
            auth_token=beeminder_auth_token,
            target_goal=target_goal
        )


def main():
    parser = argparse.ArgumentParser(
        description=(
            'Put overdue tasks from todoist into a beeminder goal each day'
        )
    )
    parser.add_argument('--beeminder-auth-token', type=str, required=True,
                        help='The API key to use for beeminder')
    parser.add_argument('--todoist-auth-token', type=str, required=True,
                        help='The API key to use for beeminder')
    parser.add_argument('--target-goal', type=str, default='todoist',
                        help='The beeminder goal to post to')
    args = parser.parse_args()

    import_overdue_tasks(**vars(args))

if __name__ == '__main__':
    main()
