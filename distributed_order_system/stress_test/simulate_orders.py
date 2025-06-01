import requests
import random
import uuid
import time
import concurrent.futures
import argparse
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample data for order generation
REGIONS = ['HCM', 'HN', 'DN']
CUSTOMER_NAMES = [
    'Nguyen Van A', 'Tran Thi B', 'Le Van C', 
    'Pham Thi D', 'Hoang Van E', 'Vo Thi F'
]

def generate_order():
    """Generate a random order"""
    return {
        'order_id': str(uuid.uuid4()),
        'customer_name': random.choice(CUSTOMER_NAMES),
        'region': random.choice(REGIONS),
        'timestamp': datetime.utcnow().isoformat()
    }

def submit_order(airflow_endpoint):
    """Submit a single order to Airflow"""
    order = generate_order()
    try:
        response = requests.post(
            f"{airflow_endpoint}/api/v1/dags/order_workflow/dagRuns",
            json={'conf': {'order': order}},
            headers={'Content-Type': 'application/json'},
            auth=('airflow', 'airflow')  # Default Airflow credentials
        )
        response.raise_for_status()
        logger.info(f"Successfully submitted order {order['order_id']} for {order['customer_name']} in {order['region']}")
        return True
    except requests.RequestException as e:
        logger.error(f"Failed to submit order: {e}")
        return False

def run_stress_test(num_orders, concurrency, airflow_endpoint):
    """Run stress test with concurrent order submissions"""
    logger.info(f"Starting stress test with {num_orders} orders and concurrency level {concurrency}")
    start_time = time.time()
    successful_orders = 0
    failed_orders = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [
            executor.submit(submit_order, airflow_endpoint)
            for _ in range(num_orders)
        ]
        
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                successful_orders += 1
            else:
                failed_orders += 1

    end_time = time.time()
    duration = end_time - start_time
    
    # Print summary
    logger.info("\n=== Stress Test Results ===")
    logger.info(f"Total Orders: {num_orders}")
    logger.info(f"Successful Orders: {successful_orders}")
    logger.info(f"Failed Orders: {failed_orders}")
    logger.info(f"Total Duration: {duration:.2f} seconds")
    logger.info(f"Average Rate: {num_orders/duration:.2f} orders/second")
    logger.info("========================")

def main():
    parser = argparse.ArgumentParser(description='Order Management System Stress Test')
    parser.add_argument('--orders', type=int, default=1000,
                      help='Number of orders to generate (default: 1000)')
    parser.add_argument('--concurrency', type=int, default=10,
                      help='Number of concurrent submissions (default: 10)')
    parser.add_argument('--endpoint', type=str, 
                      default='http://localhost:8080',
                      help='Airflow API endpoint (default: http://localhost:8080)')
    
    args = parser.parse_args()
    
    try:
        run_stress_test(args.orders, args.concurrency, args.endpoint)
    except KeyboardInterrupt:
        logger.info("\nStress test interrupted by user")
    except Exception as e:
        logger.error(f"Stress test failed: {e}")

if __name__ == '__main__':
    main()
