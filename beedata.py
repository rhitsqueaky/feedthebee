import argparse
from backpressure import all_goals
from operator import itemgetter
from truncatedgoals import get_datapoints
from datetime import datetime


def all_data(auth_token):
    goals = all_goals(auth_token=auth_token)
    goal_slugs = map(itemgetter('slug'), goals)
    datapoints = []
    for slug in goal_slugs:
        ds = get_datapoints(auth_token=auth_token, goal=slug)
        for d in ds:
            d["goal"] = slug
            d["timestamp"] = datetime.utcfromtimestamp(d["timestamp"])
        datapoints.extend(ds)
    datapoints.sort(key=itemgetter('timestamp'))
    return datapoints


def main():
    parser = argparse.ArgumentParser(
        description="List all data you've entered into beeminder"
    )
    parser.add_argument('--auth-token', type=str, required=True,
                        help='The API key to use for beeminder')
    args = parser.parse_args()

    for d in all_data(**vars(args)):
        when = d["timestamp"]
        print '\t'.join(map(str, (when, d["goal"], d["value"], d["comment"])))


if __name__ == '__main__':
    main()
