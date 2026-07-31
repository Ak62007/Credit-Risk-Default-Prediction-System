import json
from pathlib import Path
from locust import HttpUser, between, task

# loading the payload
cwd = Path.cwd()

with open(cwd / 'test_payload.json', 'r') as f:
    payload = json.load(f)

class User(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def predict(self):
        self.client.post('/predict', json=payload)