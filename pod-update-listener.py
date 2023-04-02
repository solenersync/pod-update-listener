import os
import json
import requests
from kubernetes import client, config, watch
import time
import sys

last_image_ids = {}

def main():
    config.load_incluster_config()
    # config.load_kube_config() //local
    v1 = client.CoreV1Api()
    namespace = "default"
    pods_to_watch = ["ses-demo", "pv-service", "ses-front-end", "solar-array-store", "user-store"]

    while True:
      try:
        w = watch.Watch()
        for event in w.stream(v1.list_namespaced_pod, namespace):
            print(event['object'].metadata.name)
            sys.stdout.flush()
            if any(pod_name in event['object'].metadata.name for pod_name in pods_to_watch):
              pod_name = event['object'].metadata.name
              print(f"in here with pod name: {pod_name}")
              if event['type'] == "MODIFIED" and event['object'].status.container_statuses:
                  print(f"in here with event type: {event['type']}")
                  print(f"in here with event status: {event['object'].status.container_statuses}")
                  for container_status in event['object'].status.container_statuses:
                      container_name = container_status.name
                      current_image_id = container_status.image_id
                      print(f"container_status.ready: {container_status.ready}")
                      print(f"container status image id: {container_status.image_id}")
                      print(f"current image id: {current_image_id}")
                      
                      if container_status.ready and container_status.image_id == current_image_id:
                          last_image_id = last_image_ids.get(f"{pod_name}-{container_name}")
                          print(f"in here ... READY last image id: {last_image_id}")
                          print(f"in here ... READY current image id: {current_image_id}")
                          
                          if last_image_id is None or last_image_id != current_image_id:
                              last_image_ids[f"{pod_name}-{container_name}"] = current_image_id
                              trigger_github_actions_workflow()
      except Exception as e:
        print(f"Stream closed with error: {e}")
        sys.stdout.flush()
        time.sleep(5)  # Wait for 5 seconds before restarting the watch stream

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
        sys.stdout.flush()
    else:
        print(f"Failed to trigger GitHub Actions workflow. Response: {response.text}")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
