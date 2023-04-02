import os
import json
import requests
from kubernetes import client, config, watch

def main():
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    namespace = "default" 

    w = watch.Watch()
    for event in w.stream(v1.list_namespaced_pod, namespace):
        if event['type'] == "MODIFIED" and event['object'].status.container_statuses:
            for container_status in event['object'].status.container_statuses:
                if container_status.image != container_status.image_id:
                    trigger_github_actions_workflow()
                    break

def trigger_github_actions_workflow():
    GITHUB_REPO = os.environ['GITHUB_REPO']
    GITHUB_TOKEN = os.environ['GITHUB_TOKEN']

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}"
    }

    url = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"

    payload = {
        "event_type": "pod_updated",
        "client_payload": {}
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 204:
        print("GitHub Actions workflow triggered successfully.")
    else:
        print(f"Failed to trigger GitHub Actions workflow. Response: {response.text}")

if __name__ == "__main__":
    main()
