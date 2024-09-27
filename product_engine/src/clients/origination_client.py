import requests

from models.schemas import ApplicationRequest

class OriginationClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        
    def post_application(self, application: ApplicationRequest):
        url = f"{self.base_url}/application"
        try:
            response = self.session.post(url, json=application.model_dump())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None