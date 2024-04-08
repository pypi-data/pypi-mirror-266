import pymongo
import configparser
from .event_helper import *
config = configparser.ConfigParser()
config.read("config.ini")


def change_id_to_mongo_id(data):
    data["_id"] = data["id"]
    del data["id"]
    return data


def change_mongo_id_to_id(data):
    data["id"] = data["_id"]
    del data["_id"]
    return data


def persist_value(table, key, value):
    connection_string = config["db"][
        "connection_string"
    ]  # Primary or secondary access key
    client = pymongo.MongoClient(connection_string)
    client_table = client["caas"][table]
    value = change_id_to_mongo_id(value)
    client_table.replace_one({"_id": key}, value, upsert=True)
    value = change_mongo_id_to_id(value)
    client.close()


def get_table_values(table, key):
    connection_string = config["db"][
        "connection_string"
    ]  # Primary or secondary access key
    client = pymongo.MongoClient(connection_string)
    client_table = client["caas"][table]
    data = client_table.find_one({"_id": key})
    data = change_mongo_id_to_id(data)
    client.close()
    return data


def delete_table_values(table, key):
    connection_string = config["db"][
        "connection_string"
    ]  # Primary or secondary access key
    client = pymongo.MongoClient(connection_string)
    client_table = client["caas"][table]
    client_table.delete_one({"_id": key})
    client.close()


def get_all_values_from_interim_jobs(table):
    connection_string = config["db"][
        "connection_string"
    ]  # Primary or secondary access key
    client = pymongo.MongoClient(connection_string)
    client_table = client["caas"][table]
    data = client_table.find({})
    all_ids = []
    for job in data:
        all_ids.append(job["_id"])
    return all_ids


def get_levels_for_block(table, task_id, algo_name):
    connection_string = config["db"][
        "connection_string"
    ]  # Primary or secondary access key
    client = pymongo.MongoClient(connection_string)
    client_table = client["caas"][table]
    data = client_table.find(
        {"$and": [{"task_id": task_id}, {"algo_block": algo_name}]}
    )
    all_levels = []
    for i in data:
        all_levels.append(i["level"])
    return all_levels


def get_interim_tasks(table, task_id, algo_name, level):
    connection_string = config["db"][
        "connection_string"
    ]  # Primary or secondary access key
    client = pymongo.MongoClient(connection_string)
    client_table = client["caas"][table]
    data = client_table.find_one(
        {"$and": [{"task_id": task_id}, {"algo_block": algo_name}, {"level": level}]}
    )
    data = change_mongo_id_to_id(data)
    client.close()
    return data


def check_status_of_algo_block(table, task_id, algo_name):
    connection_string = config["db"][
        "connection_string"
    ]  # Primary or secondary access key
    client = pymongo.MongoClient(connection_string)
    client_table = client["caas"][table]
    data = client_table.find(
        {"$and": [{"task_id": task_id}, {"algo_block": algo_name}]}
    )
    for i in data:
        if i["last_block"] == 0:
            return False
        if "status" in i:
            if i["status"] == "FAILED":
                return False
        else:
            return False
    return True


def mark_dependant_as_failed(table, task_id, url):
    connection_string = config["db"][
        "connection_string"
    ]  # Primary or secondary access key
    client = pymongo.MongoClient(connection_string)
    client_table = client["caas"][table]
    data = client_table.find({"$and": [{"task_id": task_id}]})
    for i in data:
        i = change_mongo_id_to_id(i)
        if 'status' not in i:
            i['status'] = 'FAILED'
            if 'caas_job_id' in i:
                stop_caas_job(url,i['caas_job_id'])
        persist_value(table,i['id'],i)
    client.close()
