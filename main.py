from base64 import b64decode
import json
import requests


GOOGLE_CHAT_WEBHOOK_URL = 'https://chat.googleapis.com/v1/spaces/xxxxxxxxxxx/messages?key=xxxxxxxxxxx...'
MESSAGE_TEMPLATE = """
{{
    "cards": [
        {{
            "header": {{
                "title": "<users/all> Google Cloud Monitoring Alert"
            }},
            "sections": [
                {{
                    "header": "{incident[policy_name]}",
                    "widgets": [
                        {{
                            "textParagraph": {{
                                "text": "{incident[summary]}"
                            }}
                        }}
                    ]
                }},
                {{
                    "widgets": [
                        {{
                            "keyValue": {{
                                "topLabel": "Status",
                                "content": "{incident[state]}"
                            }}
                        }}
                    ]
                }},
                {{
                    "widgets": [
                        {{
                            "buttons": [
                                {{
                                    "textButton": {{
                                        "text": "GO TO INCIDENT",
                                        "onClick": {{
                                            "openLink": {{
                                                "url": "{incident[url]}"
                                            }}
                                        }}
                                    }}
                                }}
                            ]
                        }}
                    ]
                }}
            ]
        }}
    ]
}}
"""  # https://docs.python.org/3/library/string.html#format-string-syntax


def monitoring_alerts(event, *_):
    """
    Forwards a Cloud Monitoring alert to the Google Chat.
    """
    # get Pub/Sub payload
    alert = json.loads(b64decode(event['data']).decode('utf-8'))
    # replace placeholders in message template
    message = json.loads(MESSAGE_TEMPLATE.format(**alert))
    # post the message to the Google Chat webhook
    requests.post(GOOGLE_CHAT_WEBHOOK_URL, json=message)


if __name__ == '__main__':
    from base64 import b64encode
    from flask import Flask, request

    GOOGLE_CHAT_WEBHOOK_URL = 'http://0.0.0.0:8080/fake-webhook'
    alert = """
        {
          "incident": {
            "incident_id": "0.opqiw61fsv7p",
            "scoping_project_id": "internal-project",
            "scoping_project_number": 12345,
            "url": "https://console.cloud.google.com/monitoring/alerting/incidents/0.lxfiw61fsv7p?project=internal-project",
            "started_at": 1577840461,
            "ended_at": 1577877071,
            "state": "closed",
            "resource_id": "11223344",
            "resource_name": "internal-project gke-cluster-1-default-pool-e2df4cbd-dgp3",
            "resource_display_name": "gke-cluster-1-default-pool-e2df4cbd-dgp3",
            "resource_type_display_name": "VM Instance",
            "resource": {
              "type": "gce_instance",
              "labels": {
                "instance_id": "11223344",
                "project_id": "internal-project",
                "zone": "us-central1-c"
              }
            },
            "metric": {
              "type": "compute.googleapis.com/instance/cpu/utilization",
              "displayName": "CPU utilization",
              "labels": {
                "instance_name": "the name of the VM instance"
              }
            },
            "metadata": {
              "system_labels": { "labelkey": "labelvalue" },
              "user_labels": { "labelkey": "labelvalue" }
            },
            "policy_name": "Monitor-Project-Cluster",
            "policy_user_labels" : {
                "user-label-1" : "important label",
                "user-label-2" : "another label"
            },
            "condition_name": "VM Instance - CPU utilization [MAX]",
            "threshold_value": "0.9",
            "observed_value": "0.835",
            "condition": {
              "name": "projects/internal-project/alertPolicies/1234567890123456789/conditions/1234567890123456789",
              "displayName": "VM Instance - CPU utilization [MAX]",
              "conditionThreshold": {
                "filter": "metric.type=\\"compute.googleapis.com/instance/cpu/utilization\\" resource.type=\\"gce_instance\\" metadata.system_labels.\\"state\\"=\\"ACTIVE\\"",
                "aggregations": [
                  {
                    "alignmentPeriod": "120s",
                    "perSeriesAligner": "ALIGN_MEAN"
                  }
                ],
                "comparison": "COMPARISON_GT",
                "thresholdValue": 0.9,
                "duration": "0s",
                "trigger": {
                  "count": 1
                }
              }
            },
            "documentation": {
              "content": "TEST ALERT",
              "mime_type": "text/markdown"
            },
            "summary": "CPU utilization for internal-project gke-cluster-1-16-default-pool-e2df4cbd-dgp3 with metric labels {instance_name=gke-cluster-1-default-pool-e2df4cbd-dgp3} and system labels {state=ACTIVE} returned to normal with a value of 0.835."
          },
          "version": "1.2"
        }"""

    def _wrapper(fnc):
        def _wrapped(**kwargs):
            fnc(**kwargs)
            return '', 204
        return _wrapped

    localhost = Flask(__name__)
    localhost.add_url_rule('/monitoring-alerts', 'monitoring_alerts', _wrapper(monitoring_alerts), methods=['POST'], defaults={'event': {'data': b64encode(alert.encode())}})
    localhost.add_url_rule('/fake-webhook', 'webhook', _wrapper(lambda: print(request.get_json())), methods=['POST'])
    localhost.run(debug=True, host='0.0.0.0', port=8080)
