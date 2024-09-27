import requests

class ProductEngineClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()


    def get_all_active_agreements_by_client(self, client_id: int):
        url = f"{self.base_url}/agreement/{client_id}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None
        