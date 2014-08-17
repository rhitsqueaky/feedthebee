import requests
import json


def submit_datapoints(target_goal, auth_token, datapoints):
    if datapoints:
        api_url = (
            "https://www.beeminder.com/api/v1/users/me/goals/%s/"
            "datapoints/create_all.json"
        ) % (
            target_goal,
        )

        response = requests.post(api_url, data={
            'datapoints': json.dumps(datapoints),
            'auth_token': auth_token
        })

        result = json.loads(response.text)
        if isinstance(result, dict) and result.get('errors'):
            raise ValueError(
                [json.loads(e)["comment"] for e in result["errors"]])
