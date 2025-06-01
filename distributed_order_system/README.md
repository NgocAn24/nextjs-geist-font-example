# Distributed Order Management System

A distributed order management system built with Apache Airflow for workflow orchestration and Flask for warehouse node APIs. The system demonstrates distributed computing concepts including fault tolerance, sharding, and load balancing.

## System Architecture

```
                            [ Client ]
                                |
                                v
                     [ API Gateway / Frontend ]
                                |
                                v
                    +-------------------------+
                    | Apache Airflow Scheduler |
                    +-------------------------+
                                |
                 +--------------+--------------+
                 |              |              |
         [Node Kho HCM]   [Node Kho HN]   [Node Kho Đà Nẵng]
              Flask API       Flask API         Flask API
                 |               |                 |
            SQLite/Postgres   SQLite/Postgres   SQLite/Postgres
```

## Features

- **Distributed Processing**: Orders are distributed across multiple warehouse nodes
- **Fault Tolerance**: System continues operating if a node fails
- **Regional Sharding**: Orders are assigned to warehouses based on region
- **Load Balancing**: Orders can be redirected to less busy nodes
- **Health Monitoring**: Each node exposes health metrics
- **Stress Testing**: Includes tools for load testing

## Components

1. **Airflow DAG**
   - Orchestrates order workflow
   - Handles node assignment and failover
   - Monitors order processing status

2. **Warehouse Nodes**
   - Flask APIs for order processing
   - SQLite database for order storage
   - Health check endpoints
   - Regional-specific processing

3. **Stress Testing**
   - Simulates high-volume order submission
   - Concurrent request handling
   - Performance metrics collection

## Setup Instructions

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Network connectivity between containers

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd distributed_order_system
   ```

2. **Start Airflow**
   ```bash
   cd airflow
   docker-compose up -d
   ```
   Access Airflow UI at http://localhost:8080 (default credentials: airflow/airflow)

3. **Start Warehouse Nodes**
   ```bash
   cd ../warehouse_node
   docker-compose up -d
   ```
   This will start three warehouse nodes:
   - HCM Node: http://localhost:5001
   - HN Node: http://localhost:5002
   - DN Node: http://localhost:5003

4. **Run Stress Test**
   ```bash
   cd ../stress_test
   python simulate_orders.py --orders 1000 --concurrency 10
   ```

## API Endpoints

### Warehouse Node APIs

1. **Health Check**
   ```
   GET /health
   ```

2. **Create Order**
   ```
   POST /order
   {
     "order_id": "uuid",
     "customer_name": "string",
     "region": "string"
   }
   ```

3. **List Orders**
   ```
   GET /orders
   ```

4. **Get Order**
   ```
   GET /order/<order_id>
   ```

## Monitoring

1. **Airflow Dashboard**
   - Monitor DAG runs
   - View task success/failure
   - Check system logs

2. **Node Health**
   - Each node exposes metrics via /health
   - Monitor order processing load
   - Check node status

## Error Handling

- Failed orders are automatically retried
- Node failures trigger failover to available nodes
- All errors are logged for debugging

## Performance Testing

Use the stress test script with different parameters:

```bash
python simulate_orders.py --orders 1000 --concurrency 10 --endpoint http://localhost:8080
```

## Development

### Adding New Features

1. **New Warehouse Node**
   - Copy existing node directory
   - Update configuration
   - Add to docker-compose.yml

2. **Custom Processing Logic**
   - Modify warehouse node app.py
   - Update Airflow DAG as needed

### Debugging

1. **View Logs**
   ```bash
   # Airflow logs
   docker-compose logs -f airflow-webserver

   # Warehouse node logs
   docker-compose logs -f node-hcm
   ```

2. **Check Node Health**
   ```bash
   curl http://localhost:5001/health
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License

## Support

For issues and questions, please create an issue in the repository.
