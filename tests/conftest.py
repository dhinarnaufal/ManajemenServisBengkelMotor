import itertools

import pytest
from fastapi.testclient import TestClient

from app.repositories import memory
from main import app

API_KEY = "bengkel-dev-key"


@pytest.fixture(autouse=True)
def clean_store():
    memory.reset_store()
    yield
    memory.reset_store()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers():
    return {"X-API-Key": API_KEY}


class Api:
    """Pembantu kecil agar tes API ringkas dan mudah dibaca."""

    def __init__(self, client, headers):
        self.client = client
        self.headers = headers
        self._plates = itertools.count(1000)

    def get(self, url, params=None):
        return self.client.get(url, headers=self.headers, params=params)

    def post(self, url, json=None):
        return self.client.post(url, headers=self.headers, json=json)

    def patch(self, url, json=None):
        return self.client.patch(url, headers=self.headers, json=json)

    def customer(self, **override):
        payload = {"name": "Andi Saputra", "phone": "081234567890", **override}
        response = self.post("/api/v1/customers", payload)
        assert response.status_code == 201, response.text
        return response.json()

    def vehicle(self, customer_id=None, **override):
        if customer_id is None:
            customer_id = self.customer()["id"]
        payload = {
            "customer_id": customer_id,
            "plate_number": "DD {} AB".format(next(self._plates)),
            "brand": "Honda",
            "model": "Beat",
            "year": 2020,
            **override,
        }
        response = self.post("/api/v1/vehicles", payload)
        assert response.status_code == 201, response.text
        return response.json()

    def mechanic(self, **override):
        payload = {"name": "Budi", "specialty": "Mesin", **override}
        response = self.post("/api/v1/mechanics", payload)
        assert response.status_code == 201, response.text
        return response.json()

    def sparepart(self, **override):
        payload = {"name": "Oli Mesin 1L", "price": 50000, "stock": 10, **override}
        response = self.post("/api/v1/spareparts", payload)
        assert response.status_code == 201, response.text
        return response.json()

    def order(self, vehicle_id=None, mechanic_id=None, **override):
        if vehicle_id is None:
            vehicle_id = self.vehicle()["id"]
        if mechanic_id is None:
            mechanic_id = self.mechanic()["id"]
        payload = {
            "vehicle_id": vehicle_id,
            "mechanic_id": mechanic_id,
            "complaint": "Mesin brebet saat digas",
            "labor_cost": 100000,
            **override,
        }
        return self.post("/api/v1/services", payload)


@pytest.fixture
def api(client, auth_headers):
    return Api(client, auth_headers)
