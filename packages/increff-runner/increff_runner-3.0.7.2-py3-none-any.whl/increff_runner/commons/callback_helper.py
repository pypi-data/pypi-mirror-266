from logging_increff.function import *
from .mse_helper import create_events_for_next_blocks, mark_dependant_as_failed
from .constants import *
import requests
import json
from .db_service import update_job
from .db_helper import get_interim_tasks


def send_success_callback(url, output, error_data, job):
    if error_data != {}:
        send_failure_callback(url, "Script Failed", output, error_data, job)
        return
    output["caas_job_id"] = job["id"]
    add_info_logs(job["id"], "Hitting Success Callback")
    body = {
        "StatusCode": "200",
        "Output": {"output_data": output, "error_data": error_data},
    }
    add_info_logs(job["id"], f"Success message -> {str(body)}")
    job["callback_status"] = "200"
    update_job(job)
    response = requests.post(url, data=json.dumps(body))


def send_success_webhook(url, master_url, output, error_data, job):
    if error_data != {}:
        send_failure_webhook(master_url, job["data"]["task_id"], error_data, job)
        return
    
    output["caas_job_id"] = job["id"]
    add_info_logs(job["id"], "Hitting Success WebHook Callback")
    create_events_for_next_blocks(url, master_url, output, error_data, job)


def send_failure_callback(url, error, output_data, error_data, job):
    add_info_logs(job["id"], "Hitting Failure Callback")
    output_data["caas_job_id"] = job["id"]
    body = {
        "Output": {"output_data": output_data, "error_data": error_data},
        "Error": {"ErrorCode": "400", "Message": str(error)},
        "StatusCode": "400",
    }
    add_info_logs(job["id"], f" failure message -> {str(body)}")
    job["callback_status"] = 400
    update_job(job)
    response = requests.post(url, data=json.dumps(body))


def send_failure_webhook(url, task_id, error, job):
    interim_task = get_interim_tasks(INTERIM_TASK_TABLE, task_id, job["data"]["algo_name"], job["data"]["level"])
    data = {"status": "FAILED", "taskId": task_id, "subtaskName":  interim_task['parent_task'],"reason":str(error)}

    # TODO @jaynit to move this config at the client level
    headers = {
        "Content-Type": "application/json",
        "authUsername":"caas-user@increff.com",
        "authPassword":"caasuser@123",
        "authdomainname": job["data"]["client"],
        "Conection":"keep-alive"
    }
    add_info_logs(job["id"], f" failure message -> {str(data)}")
    job["webhook_status"] = 400
    update_job(job)
    
    # TODO @jaynit ensure that they are not moved to Success again #cr1_unni
    # TODO @jaynit kill the kube jobs also if it is running #cr1_unni
    mark_dependant_as_failed(INTERIM_TASK_TABLE,task_id,job["data"]["webHookUri"])
    response = requests.put(url, params=data,headers=headers)
