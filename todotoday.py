"""
Integration between todoist and beeminder in the other direction. Create todo
items to work on beeminder tasks.

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

from backpressure import impending_goals
import random
import requests
import argparse

def tasks_to_work_on(beeminder_token):
    goals = list(impending_goals(beeminder_token, 14))
    if not goals:
        return []

    urgent_goals = [(g, 4) for g, d in goals if g <= 3]
    if urgent_goals:
        return urgent_goals

    pressing_goals = [(g, 2) for g, d in goals if g <= 7]
    if pressing_goals:
        return pressing_goals
    
    return [(random.choice(goals)[0], 1)] 


def submit_the_daily_tasks(todoist_auth_token, beeminder_auth_token):
    tasks = tasks_to_work_on(beeminder_auth_token)

    for task, urgency in tasks:
        response = requests.post("https://api.todoist.com/API/addItem", data={
            'token': todoist_auth_token,
            'date_string': 'today',
            'priority': str(urgency),
            'content': ("Work on beeminder goal %s" % (task,))
        })
        if response.status_code != 200:
            raise ValueError(response.text)

    
def main():
    parser = argparse.ArgumentParser(
        description=(
            'Put goals from beeminder into todoist tasks each day'
        )
    )
    parser.add_argument('--beeminder-auth-token', type=str, required=True,
                        help='The API key to use for beeminder')
    parser.add_argument('--todoist-auth-token', type=str, required=True,
                        help='The API key to use for beeminder')
    args = parser.parse_args()

    submit_the_daily_tasks(**vars(args))

if __name__ == '__main__':
    main()
