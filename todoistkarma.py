"""
Integration between todoist and beeminder. Takes karma from todoist and puts
it into a beeminder goal.

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


def get_karma(todoist_auth_token):
    return json.loads(
        requests.get(
            "https://api.todoist.com/API/getProductivityStats",
            params={
                'token': todoist_auth_token,
            }).text)['karma']


def import_karma(
    todoist_auth_token, beeminder_auth_token, target_goal
):
    now = time()
    karma = get_karma(todoist_auth_token)
    beeminder.submit_datapoints(
        datapoints=[{
            'value': karma,
            'timestamp': now,
        }],
        auth_token=beeminder_auth_token,
        target_goal=target_goal
    )


def main():
    parser = argparse.ArgumentParser(
        description=(
            'Put karma from todoist into a beeminder goal'
        )
    )
    parser.add_argument('--beeminder-auth-token', type=str, required=True,
                        help='The API key to use for beeminder')
    parser.add_argument('--todoist-auth-token', type=str, required=True,
                        help='The API key to use for beeminder')
    parser.add_argument('--target-goal', type=str, default='todoistkarma',
                        help='The beeminder goal to post to')
    args = parser.parse_args()

    import_karma(**vars(args))

if __name__ == '__main__':
    main()
