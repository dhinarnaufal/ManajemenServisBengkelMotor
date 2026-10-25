BASE = "/api/v1"


# ---------- umum & auth ----------
def test_root_is_public(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "Manajemen Servis Bengkel Motor"


def test_endpoint_requires_api_key(client):
    assert client.get(BASE + "/customers").status_code == 401


def test_endpoint_rejects_wrong_api_key(client):
    response = client.get(BASE + "/customers", headers={"X-API-Key": "salah"})
    assert response.status_code == 401


# ---------- pelanggan ----------
def test_create_and_get_customer(api):
    created = api.customer()
    assert created["id"] == 1
    response = api.get(BASE + "/customers/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Andi Saputra"


def test_customer_invalid_phone_rejected(api):
    response = api.post(BASE + "/customers", {"name": "Andi", "phone": "abc"})
    assert response.status_code == 422


def test_customer_extra_field_rejected(api):
    payload = {"name": "Andi", "phone": "081234567890", "role": "admin"}
    assert api.post(BASE + "/customers", payload).status_code == 422


def test_customer_not_found(api):
    response = api.get(BASE + "/customers/99")
    assert response.status_code == 404
    assert response.json()["error_code"] == "NOT_FOUND"


# ---------- kendaraan ----------
def test_create_vehicle_normalizes_plate(api):
    customer = api.customer()
    vehicle = api.vehicle(customer["id"], plate_number="dd  1234   ab")
    assert vehicle["plate_number"] == "DD 1234 AB"


def test_vehicle_unknown_customer_returns_404(api):
    payload = {
        "customer_id": 99,
        "plate_number": "DD 1 A",
        "brand": "Honda",
        "model": "Beat",
        "year": 2020,
    }
    assert api.post(BASE + "/vehicles", payload).status_code == 404


def test_vehicle_duplicate_plate_returns_409(api):
    customer = api.customer()
    api.vehicle(customer["id"], plate_number="DD 1234 AB")
    payload = {
        "customer_id": customer["id"],
        "plate_number": "DD1234AB",
        "brand": "Yamaha",
        "model": "NMAX",
        "year": 2022,
    }
    assert api.post(BASE + "/vehicles", payload).status_code == 409


def test_vehicle_invalid_plate_rejected(api):
    customer = api.customer()
    payload = {
        "customer_id": customer["id"],
        "plate_number": "!!!???",
        "brand": "Honda",
        "model": "Beat",
        "year": 2020,
    }
    assert api.post(BASE + "/vehicles", payload).status_code == 422


def test_list_vehicles_filter_by_customer(api):
    first, second = api.customer(), api.customer(name="Siti Aminah")
    api.vehicle(first["id"])
    api.vehicle(second["id"])
    response = api.get(BASE + "/vehicles", {"customer_id": first["id"]})
    assert len(response.json()) == 1


# ---------- sparepart ----------
def test_create_sparepart_and_duplicate_name(api):
    api.sparepart(name="Busi")
    payload = {"name": "BUSI", "price": 20000, "stock": 5}
    assert api.post(BASE + "/spareparts", payload).status_code == 409


def test_restock_adds_stock(api):
    part = api.sparepart(stock=5)
    response = api.post("{}/spareparts/{}/restock".format(BASE, part["id"]), {"quantity": 7})
    assert response.status_code == 200
    assert response.json()["stock"] == 12


def test_sparepart_negative_stock_rejected(api):
    payload = {"name": "Busi", "price": 20000, "stock": -1}
    assert api.post(BASE + "/spareparts", payload).status_code == 422


# ---------- mekanik ----------
def test_new_mechanic_has_no_active_services(api):
    mechanic = api.mechanic()
    assert mechanic["active_services"] == 0
    assert mechanic["max_active_services"] == 3
    assert mechanic["available"] is True


# ---------- servis ----------
def test_create_service_starts_as_antri(api):
    response = api.order(labor_cost=100000)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "antri"
    assert body["parts"] == []
    assert body["total_cost"] == 100000


def test_create_service_unknown_vehicle_returns_404(api):
    mechanic = api.mechanic()
    response = api.order(vehicle_id=99, mechanic_id=mechanic["id"])
    assert response.status_code == 404


def test_create_service_unknown_mechanic_returns_404(api):
    vehicle = api.vehicle()
    response = api.order(vehicle_id=vehicle["id"], mechanic_id=99)
    assert response.status_code == 404


def test_add_part_reduces_stock_and_updates_total(api):
    part = api.sparepart(price=50000, stock=10)
    order = api.order(labor_cost=100000).json()

    response = api.post(
        "{}/services/{}/parts".format(BASE, order["id"]),
        {"sparepart_id": part["id"], "quantity": 2},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["parts_total"] == 100000
    assert body["total_cost"] == 200000  # jasa 100.000 + sparepart 100.000
    assert body["parts"][0]["subtotal"] == 100000

    assert api.get("{}/spareparts/{}".format(BASE, part["id"])).json()["stock"] == 8


def test_adding_same_part_twice_merges_line(api):
    part = api.sparepart(price=10000, stock=10)
    order = api.order(labor_cost=0).json()
    url = "{}/services/{}/parts".format(BASE, order["id"])
    api.post(url, {"sparepart_id": part["id"], "quantity": 1})
    body = api.post(url, {"sparepart_id": part["id"], "quantity": 2}).json()
    assert len(body["parts"]) == 1
    assert body["parts"][0]["quantity"] == 3
    assert body["total_cost"] == 30000


def test_add_part_insufficient_stock_returns_409_and_keeps_stock(api):
    part = api.sparepart(stock=1)
    order = api.order().json()
    response = api.post(
        "{}/services/{}/parts".format(BASE, order["id"]),
        {"sparepart_id": part["id"], "quantity": 5},
    )
    assert response.status_code == 409
    assert response.json()["error_code"] == "INSUFFICIENT_STOCK"
    assert api.get("{}/spareparts/{}".format(BASE, part["id"])).json()["stock"] == 1
    assert api.get("{}/services/{}".format(BASE, order["id"])).json()["parts"] == []


def test_add_unknown_sparepart_returns_404(api):
    order = api.order().json()
    response = api.post(
        "{}/services/{}/parts".format(BASE, order["id"]),
        {"sparepart_id": 99, "quantity": 1},
    )
    assert response.status_code == 404


def test_full_status_flow(api):
    order = api.order().json()
    url = "{}/services/{}/status".format(BASE, order["id"])
    for expected in ("dikerjakan", "selesai", "dibayar"):
        response = api.patch(url, {"status": expected})
        assert response.status_code == 200
        assert response.json()["status"] == expected


def test_status_cannot_skip_steps(api):
    order = api.order().json()
    url = "{}/services/{}/status".format(BASE, order["id"])
    response = api.patch(url, {"status": "selesai"})
    assert response.status_code == 409
    assert response.json()["error_code"] == "INVALID_STATUS_TRANSITION"


def test_status_cannot_go_backwards(api):
    order = api.order().json()
    url = "{}/services/{}/status".format(BASE, order["id"])
    api.patch(url, {"status": "dikerjakan"})
    assert api.patch(url, {"status": "antri"}).status_code == 409


def test_unknown_status_value_rejected(api):
    order = api.order().json()
    url = "{}/services/{}/status".format(BASE, order["id"])
    assert api.patch(url, {"status": "batal"}).status_code == 422


def test_cannot_add_part_after_selesai(api):
    part = api.sparepart()
    order = api.order().json()
    status_url = "{}/services/{}/status".format(BASE, order["id"])
    api.patch(status_url, {"status": "dikerjakan"})
    api.patch(status_url, {"status": "selesai"})
    response = api.post(
        "{}/services/{}/parts".format(BASE, order["id"]),
        {"sparepart_id": part["id"], "quantity": 1},
    )
    assert response.status_code == 409


def test_list_services_filters_by_status(api):
    first = api.order().json()
    api.order()
    api.patch("{}/services/{}/status".format(BASE, first["id"]), {"status": "dikerjakan"})
    response = api.get(BASE + "/services", {"status": "dikerjakan"})
    assert [item["id"] for item in response.json()] == [first["id"]]


# ---------- batas servis aktif per mekanik ----------
def test_mechanic_cannot_exceed_active_limit(api):
    vehicle = api.vehicle()
    mechanic = api.mechanic()
    for _ in range(3):
        assert api.order(vehicle["id"], mechanic["id"]).status_code == 201

    response = api.order(vehicle["id"], mechanic["id"])
    assert response.status_code == 409
    assert response.json()["error_code"] == "MECHANIC_AT_CAPACITY"

    info = api.get("{}/mechanics/{}".format(BASE, mechanic["id"])).json()
    assert info["active_services"] == 3
    assert info["available"] is False


def test_finishing_a_service_frees_mechanic_capacity(api):
    vehicle = api.vehicle()
    mechanic = api.mechanic()
    orders = [api.order(vehicle["id"], mechanic["id"]).json() for _ in range(3)]

    status_url = "{}/services/{}/status".format(BASE, orders[0]["id"])
    api.patch(status_url, {"status": "dikerjakan"})
    api.patch(status_url, {"status": "selesai"})

    assert api.order(vehicle["id"], mechanic["id"]).status_code == 201


def test_limit_is_configurable_via_env(api, monkeypatch):
    monkeypatch.setenv("BENGKEL_MAX_ACTIVE_SERVICES", "1")
    vehicle = api.vehicle()
    mechanic = api.mechanic()
    assert api.order(vehicle["id"], mechanic["id"]).status_code == 201
    assert api.order(vehicle["id"], mechanic["id"]).status_code == 409


def test_other_mechanic_is_not_affected_by_limit(api):
    vehicle = api.vehicle()
    busy, free = api.mechanic(), api.mechanic(name="Joko")
    for _ in range(3):
        api.order(vehicle["id"], busy["id"])
    assert api.order(vehicle["id"], free["id"]).status_code == 201
