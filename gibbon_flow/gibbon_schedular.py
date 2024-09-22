''' schedules the flow and task based on the cron operations in the yaml files'''

import yaml
import importlib
import time
from datetime import datetime, timedelta
from croniter import croniter
import importlib.util
from dask import delayed
from dask.distributed import Client
import sqlite3
import uuid

def get_jobs_from_yaml(file_name="flows_and_tasks.yaml"):
    with open(file_name, "r") as file:
        data = yaml.safe_load(file)
    return data

def execute_job(entry_point):
    start_time = time.time()

    file_path, function_name = entry_point.split(':')
    module_name = file_path.replace('.py', '').replace('/', '.')
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    function = getattr(module, function_name)
    function()

    end_time = time.time()
    execution_time = end_time - start_time
    return execution_time

def schedule_jobs(jobs):
    # print("\n\n", jobs, '==JOBS==')
    scheduled_jobs = []
    job_queue = [(jobs, None)]

    while job_queue:
        current_jobs, parent_flow = job_queue.pop(0)

        for flow_name, flow_data in current_jobs.items():
            # print(flow_data, '==flow data==')
            cron = flow_data.get('cron', '* * * * *')
            entry_point = flow_data.get('entry_point')
            tasks = flow_data.get('tasks', [])
            nested_flows = flow_data.get('flows', {})

            # Handle nested flows
            if nested_flows:
                for nested_flow in nested_flows:
                    full_nested_flow_name = f"{flow_name}" 
                    job_queue.append(({nested_flow['name']: jobs.get(nested_flow['name'])}, full_nested_flow_name))

            # Only schedule if there's an entry point (i.e., it's an executable flow)
            if entry_point:
                full_flow_name = f"{parent_flow}.{flow_name}" if parent_flow else flow_name
                scheduled_jobs.append((cron, entry_point, full_flow_name, tasks))
                print(f"Scheduled flow '{full_flow_name}' with cron '{cron}' and entry point '{entry_point}'")

    return scheduled_jobs

@delayed
def delayed_execute_job(entry_point, flow_name, task_names):
    print(f"Executing flow '{flow_name}' at {datetime.now()}")
    execution_time = execute_job(entry_point)
    for task_name in task_names:
        job_uuid = str(uuid.uuid4())
        store_job_execution(job_uuid, flow_name, execution_time, task_name['entry_point']) 


def store_job_execution(job_uuid, flow_name, execution_time, task_name):
    con = sqlite3.connect("flow_gibbon.db")
    cur = con.cursor()
    print(job_uuid, flow_name, execution_time, task_name)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS job_executions (
            uuid TEXT PRIMARY KEY,
            flow_name TEXT,
            task_name TEXT,
            execution_time REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        INSERT INTO job_executions (uuid, flow_name, task_name, execution_time)
        VALUES (?, ?, ?, ?)
    """, (job_uuid, flow_name, task_name, execution_time))
    con.commit()
    con.close()


def run_scheduler(scheduled_jobs):
    client = Client()
    while True:
        now = datetime.now()
        jobs_to_run = []
        for cron, entry_point, flow_name, task_names in scheduled_jobs:
            if cron == '* * * * *':
                # For '* * * * *', run only once
                if not hasattr(run_scheduler, f'ran_{flow_name}'):
                    jobs_to_run.append(delayed_execute_job(entry_point, flow_name, task_names))
                    setattr(run_scheduler, f'ran_{flow_name}', True)
            else:
                cron_iter = croniter(cron, now)
                next_run = cron_iter.get_next(datetime)
                if now <= next_run < now + timedelta(minutes=1):
                    jobs_to_run.append(delayed_execute_job(entry_point, flow_name, task_names))
        if jobs_to_run:
            client.compute(jobs_to_run)


if __name__ == "__main__":
    jobs = get_jobs_from_yaml()
    scheduled_jobs = schedule_jobs(jobs)
    run_scheduler(scheduled_jobs)
