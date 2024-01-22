'''

from datetime import datetime
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.sensors.http_sensor import HttpSensor

# Define default_args for your DAG
default_args = {
    'owner': 'your_name',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),  # Adjust the start date
    'retries': 1,
}

# Create a DAG instance
dag = DAG(
    'your_dag_id',
    default_args=default_args,
    schedule_interval=None,  # Set the desired schedule interval or use None for manual triggering
    catchup=False,  # Set to False if you don't want historical DAG runs to be triggered
    tags=['your_tags'],  # Optional tags for categorization
)

# Define a task to run the Docker container
run_docker_task = DockerOperator(
    task_id='run_docker_task',
    image='your-image-name:your-tag',  # Replace with your Docker image name and tag
    api_version='auto',
    auto_remove=True,  # Remove the container after execution
    command=["python", "gcp_fetch_main.py"],  # Specify the command to run inside the container
    dag=dag,
)

# Define a task to trigger the DAG from a Google Cloud Function via Airflow REST API
trigger_dag_task = SimpleHttpOperator(
    task_id='trigger_dag_task',
    http_conn_id='http_airflow_api',  # Specify your HTTP connection ID
    method='POST',
    endpoint='/api/v1/dags/your_dag_id/dagRuns',
    data='{"conf": "your_configuration_data"}',  # Add any configuration data needed
    headers={"Content-Type": "application/json"},
    xcom_push=True,
    dag=dag,
)

# Define a sensor task to wait for the trigger to complete (optional)
wait_for_trigger_completion = HttpSensor(
    task_id='wait_for_trigger_completion',
    http_conn_id='http_airflow_api',
    method='GET',
    endpoint='/api/v1/dags/your_dag_id/dagRuns',
    request_params={"state": "success"},
    response_check=lambda response: response.json()[0]['state'] == 'success',
    poke_interval=60,  # Adjust the polling interval as needed
    timeout=3600,  # Adjust the timeout as needed
    mode='reschedule',
    dag=dag,
)

# Set task dependencies
trigger_dag_task >> wait_for_trigger_completion >> run_docker_task

if __name__ == "__main__":
    dag.cli()


'''