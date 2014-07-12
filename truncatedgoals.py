"""
A script that creates a datapoint in one goal whenever you enter a datapoint in
another goal that is under a threshold value.

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
import requests
import json


def update_truncated_goal(auth_token, threshold, target_goal, source_goal):
    result = json.loads(requests.get(
        "https://www.beeminder.com/api/v1/users/me/goals/%s/datapoints.json" %
        (source_goal,), params={
        "auth_token": auth_token
        }).text)

    target_datapoints = [
        {
            "requestid": d["id"],
            "timestamp": d["timestamp"],
            "value": 1.0,
            "comment": d["comment"]
        } for d in result if d["value"] <= threshold
    ]
    if target_datapoints:
        api_url = (
            "https://www.beeminder.com/api/v1/users/me/goals/%s/"
            "datapoints/create_all.json"
        ) % (
            target_goal,
        )

        response = requests.post(api_url, data={
            'datapoints': json.dumps(target_datapoints),
            'auth_token': auth_token
        })

        result = json.loads(response.text)
        if isinstance(result, dict) and result.get('errors'):
            raise ValueError(
                [json.loads(e)["comment"] for e in result["errors"]])


def main():
    parser = argparse.ArgumentParser(
        description=(
            'Update (target-goal) with a value of 1 for every datapoint in '
            '(source-goal) with a value of less than (threshold)'
        )
    )
    parser.add_argument('--auth-token', type=str, required=True,
                        help='The API key to use for beeminder')
    parser.add_argument('--threshold', type=float, required=True,
                        help="Record all goals with a value under this")
    parser.add_argument('--target-goal', type=str, required=True,
                        help='The beeminder goal to post to')
    parser.add_argument('--source-goal', type=str, required=True,
                        help='The beeminder goal to get datapoints from')
    args = parser.parse_args()

    update_truncated_goal(**vars(args))

if __name__ == '__main__':
    main()
