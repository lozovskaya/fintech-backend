import requests

from models.schemas import ApplicationRequestToScoring

class ScoringClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()

    def send_application_for_scoring(self, application : ApplicationRequestToScoring):
        url = f"{self.base_url}/scoring/"
        try:
            response = self.session.post(url, json=application.model_dump())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None
        
    def get_scoring_id_of_application(self, application_id: int):
        url = f"{self.base_url}/scoring/get/application_id/{application_id}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None
        
    def get_scoring_status_of_application(self, scoring_id: int):
        url = f"{self.base_url}/scoring/get/{scoring_id}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None