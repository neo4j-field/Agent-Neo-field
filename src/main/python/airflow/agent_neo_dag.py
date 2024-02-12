import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.google.cloud.operators.cloud_run import (
    CloudRunCreateJobOperator,
    CloudRunExecuteJobOperator
)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

PROJECT_ID = 'sales-eng-agent-neo-project'  # Adjust as necessary
REGION = 'us-central1'  # Adjust as necessary

dag = DAG(
    'agent_neo_dag',
    default_args=default_args,
    description='DAG for Agent Neo tasks',
    schedule_interval=timedelta(days=1),  # Adjust as necessary
    catchup=False
)

# Task to create and execute GCP Fetch Job
create_gcp_fetch_job = CloudRunCreateJobOperator(
    task_id='create_gcp_fetch_job',
    project_id=PROJECT_ID,
    region=REGION,
    job_name='agent-neo-fetch-gcp',  # Adjust as necessary
    job={},  # Define your job here. Refer to Cloud Run Job documentation for the structure
    dag=dag,
)

execute_gcp_fetch_job = CloudRunExecuteJobOperator(
    task_id='execute_gcp_fetch_job',
    project_id=PROJECT_ID,
    region=REGION,
    job_name='agent-neo-fetch-gcp',  # Adjust as necessary
    dag=dag,
)

# Task to create and execute GCP Transform Job
create_gcp_transform_job = CloudRunCreateJobOperator(
    task_id='create_gcp_transform_job',
    project_id=PROJECT_ID,
    region=REGION,
    job_name='agent-neo-transform-gcp',  # Adjust as necessary
    job={},  # Define your job here. Refer to Cloud Run Job documentation for the structure
    dag=dag,
)

execute_gcp_transform_job = CloudRunExecuteJobOperator(
    task_id='execute_gcp_transform_job',
    project_id=PROJECT_ID,
    region=REGION,
    job_name='agent-neo-transform-gcp',  # Adjust as necessary
    dag=dag,
)

# Set task dependencies
create_gcp_fetch_job >> execute_gcp_fetch_job
create_gcp_transform_job.set_upstream(execute_gcp_fetch_job)
execute_gcp_transform_job.set_upstream(create_gcp_transform_job)
