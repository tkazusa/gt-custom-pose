# -*- coding: utf-8 -*-
import json


def lambda_handler(event, context):
    """Pre labeling lambda function for custom labeling jobs"""

    # Event received
    print("Received event: " + json.dumps(event, indent=2))

    output = {
        "taskInput": {
            "taskObject": event['dataObject']},
    }

    # Response sending
    print("Response: " + json.dumps(output))

    return output
