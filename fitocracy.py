"""
A super basic scraper for getting some data out of fitocracy. It will probably
not exactly meet your needs, but it meets mine.

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
import bs4
import json
from collections import namedtuple
from dateutil import parser


Workout = namedtuple('Workout', ('url', 'date', 'actions'))
Action = namedtuple('Action', ('label', 'entries', 'note'))
Entry = namedtuple('Entry', ('description', 'points'))


class LoginError(Exception):
    pass


def fit_url(url):
    return "https://www.fitocracy.com" + url


def get_activity_stream(username, password):
    session = requests.session()
    session.headers.update({'referer': 'https://www.fitocracy.com'})
    login_page = bs4.BeautifulSoup(
        session.get(fit_url("/accounts/login")).text)
    login_form = login_page.find(
        "form",
        attrs={'id': 'username-login-form'}
    )
    post_data = {}
    for elt in login_form.find_all('input'):
        post_data[elt['name']] = elt.get('value', '')
    post_data['username'] = username
    post_data['password'] = password
    response = session.post(
        fit_url("/accounts/login/"), data=post_data
    )
    result = json.loads(response.text)
    if not result.get('success'):
        raise LoginError("Failed login. Got response %r" % (result,))
    user_id = result['id']
    workout_elts = bs4.BeautifulSoup(session.get(
        fit_url("/activity_stream/0/"), params={'user_id': str(user_id)},
        headers={
            'X-Requested-With': "XMLHttpRequest",
            'Referer': (fit_url("/profile/%s/?feed" % (username,)))
        }
    ).text).find_all(attrs={'data-ag-type': 'workout'})

    workouts = []

    for elt in workout_elts:
        time_and_link = elt.find('a', attrs={'class': 'action_time'})
        date = parser.parse(time_and_link.text)
        link = fit_url(time_and_link['href'])
        actions = []
        for action_elt in elt.find_all('div', attrs={'class': 'action'}):
            label = (
                action_elt.find(
                    'div', attrs={'class': 'action_prompt'}).text.strip())
            entries = []
            note = None 
            for li in action_elt.find('ul').find('ul').find_all('li'):
                points_elt = li.find(
                    "span", attrs={'class': 'action_prompt_points'})
                if 'stream_note' in li.get('class', ()):
                    note = li.text.strip()
                    continue
                if points_elt is None:
                    print li
                    continue
                points = int(points_elt.text.strip())
                points_elt.decompose()
                description = li.text.strip()
                entries.append(Entry(points=points, description=description))
                
            actions.append(Action(label=label, entries=entries, note=note))

        workouts.append(Workout(
            actions=actions,
            date=date,
            url=link,
        ))

    return workouts
