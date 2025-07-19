from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator

default_args = {
    'owner': 'vaas',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'sample_data_pipeline',
    default_args=default_args,
    description='A sample data pipeline for VaaS',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['vaas', 'data-pipeline'],
)

def extract_data():
    """Extract data from source systems."""
    print("Extracting data from source systems...")
    # Simulate data extraction
    return "Data extracted successfully"

def transform_data():
    """Transform the extracted data."""
    print("Transforming data...")
    # Simulate data transformation
    return "Data transformed successfully"

def load_data():
    """Load the transformed data into target systems."""
    print("Loading data into target systems...")
    # Simulate data loading
    return "Data loaded successfully"

def validate_data():
    """Validate the loaded data."""
    print("Validating data quality...")
    # Simulate data validation
    return "Data validation completed"

# Define tasks
start = DummyOperator(task_id='start', dag=dag)

extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    dag=dag,
)

validate_task = PythonOperator(
    task_id='validate_data',
    python_callable=validate_data,
    dag=dag,
)

bash_task = BashOperator(
    task_id='bash_hello',
    bash_command='echo "Hello from Airflow!"',
    dag=dag,
)

end = DummyOperator(task_id='end', dag=dag)

# Define task dependencies
start >> extract_task >> transform_task >> load_task >> validate_task >> bash_task >> end 