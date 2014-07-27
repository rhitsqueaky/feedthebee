"""
This script is superspecific to me and just runs all the scripts in here in the
manner I actually use them. You're welcome to take this verbatim if you like
but you're more likely to want to treat it as example usage.

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

import argparse
import feedthebee
import backpressure
import todoist


def main():
    parser = argparse.ArgumentParser(
        description='My beeminder automation'
    )
    parser.add_argument('--auth-token', type=str, required=True,
                        help='The API key to use for beeminder')
    parser.add_argument('--skip-feed', default=False,
                        action='store_true',
                        help="Don't update the blogging goal")
    parser.add_argument('--skip-bedtime', default=False,
                        action='store_true',
                        help="Don't update the early nights goal")
    parser.add_argument('--skip-backpressure', default=False,
                        action='store_true',
                        help="Don't update the backpressure goal")
    parser.add_argument(
        "--todoist-auth-token", type=str,
        help=(
            "The API key to use for todoist. "
            "Will skip todoist goal if absent"))

    args = parser.parse_args()
    auth_token = args.auth_token

    if not args.skip_feed:
        feedthebee.sync_feed(
            auth_token=auth_token,
            goal='blogging',
            feed="http://www.drmaciver.com/feed"
        )
    if not args.skip_backpressure:
        backpressure.apply_backpressure(
            auth_token=auth_token,
            target_goal="backpressure",
            max_days=7
        )
        backpressure.apply_backpressure(
            auth_token=auth_token,
            target_goal="backpressureharder",
            max_days=14
        )

    if args.todoist_auth_token:
        todoist.import_overdue_tasks(
            beeminder_auth_token=args.auth_token,
            todoist_auth_token=args.todoist_auth_token,
            target_goal="todoist",
        )

if __name__ == '__main__':
    main()
