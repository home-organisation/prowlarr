import requests
from defusedxml import ElementTree

if __name__ == '__main__':

    # Get apikey from config file
    tree = ElementTree.parse('/config/config.xml')
    root = tree.getroot()
    apikey = root.find('ApiKey').text

    # Perform health check and return exit code
    try:
        response = requests.get('http://localhost:9696/api/v1/health', headers={'X-Api-Key': apikey}, timeout=5)
        if response.status_code == 200:
            print("Health check passed")
            exit(0)
        else:
            print(f"Health check failed with status code: {response.status_code}")
            exit(1)
    except Exception as e:
        print(f"Health check failed with exception: {e}")
        exit(2)