import requests

def test_node_health(container_name, port, node_name):
    try:
        # Try both container name and localhost
        urls = [
            f'http://{container_name}:5000/health',
            f'http://localhost:{port}/health'
        ]
        
        for url in urls:
            try:
                print(f"\nTrying {url}")
                response = requests.get(url, timeout=5)
                print(f"{node_name} Response:")
                print(response.json())
                return
            except requests.exceptions.RequestException as e:
                print(f"Error with {url}:")
                print(str(e))

    except Exception as e:
        print(f"\n{node_name} Error:")
        print(str(e))

# Test all nodes
print("Testing warehouse nodes health...")
test_node_health('node-hcm', 5001, "HCM Node")
test_node_health('node-hn', 5002, "HN Node")
test_node_health('node-dn', 5003, "DN Node")
