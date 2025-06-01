from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
import requests
import json
import logging
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Warehouse node endpoints
WAREHOUSE_NODES = {
    'HCM': 'http://node-hcm:5000',
    'HN': 'http://node-hn:5000', 
    'DN': 'http://node-dn:5000'
}

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
}

def ingest_order(**context):
    """
    Simulate order ingestion and validation
    """
    # In real system, this would pull from a queue or API
    order = context['dag_run'].conf.get('order', {})
    if not order:
        raise ValueError("No order data provided")
    
    logger.info(f"Ingested order: {order}")
    return order

def assign_warehouse(**context):
    """
    Assign order to appropriate warehouse based on region and load
    """
    order = context['task_instance'].xcom_pull(task_ids='ingest_order')
    region = order.get('region', 'HCM')  # Default to HCM if no region specified
    
    # Check warehouse health and load
    try:
        response = requests.get(f"{WAREHOUSE_NODES[region]}/health")
        if response.status_code == 200:
            logger.info(f"Assigned to warehouse {region}")
            return region
    except requests.RequestException as e:
        logger.error(f"Error checking warehouse {region}: {e}")
    
    # Fallback: randomly choose another warehouse
    available = list(set(WAREHOUSE_NODES.keys()) - {region})
    return random.choice(available)

def process_order(**context):
    """
    Send order to assigned warehouse for processing
    """
    ti = context['task_instance']
    order = ti.xcom_pull(task_ids='ingest_order')
    assigned_warehouse = ti.xcom_pull(task_ids='assign_warehouse')
    
    warehouse_url = f"{WAREHOUSE_NODES[assigned_warehouse]}/order"
    
    try:
        response = requests.post(
            warehouse_url,
            json=order,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        logger.info(f"Order processed successfully at {assigned_warehouse}")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to process order at {assigned_warehouse}: {e}")
        raise

# Define the DAG
dag = DAG(
    'order_workflow',
    default_args=default_args,
    description='Workflow for distributed order processing',
    schedule_interval=None,  # Triggered via API
    catchup=False
)

# Define tasks
ingest_task = PythonOperator(
    task_id='ingest_order',
    python_callable=ingest_order,
    provide_context=True,
    dag=dag,
)

assign_task = PythonOperator(
    task_id='assign_warehouse',
    python_callable=assign_warehouse,
    provide_context=True,
    dag=dag,
)

process_task = PythonOperator(
    task_id='process_order',
    python_callable=process_order,
    provide_context=True,
    dag=dag,
)

# Set task dependencies
ingest_task >> assign_task >> process_task
