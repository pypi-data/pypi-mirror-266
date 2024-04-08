import json
import requests


def create_caas_job(url, data):
    data["subject"] = "mse-runner"
    response = requests.post(url, data=json.dumps(data))
    return response.json()

def stop_caas_job(url,job_id):
    data = {
        'subject':'stop-mse-runner',
        'job_id':job_id
    }
    response = requests.post(url, data=json.dumps(data))