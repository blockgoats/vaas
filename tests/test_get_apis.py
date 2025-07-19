import requests

BASE = "http://localhost:8000"

def test_get_teams():
    r = requests.get(f"{BASE}/teams/")
    assert r.status_code == 200
    assert any(team["name"] == "Test Team" for team in r.json())

def test_get_users():
    r = requests.get(f"{BASE}/users/")
    assert r.status_code == 200
    assert any(user["email"] == "testuser@example.com" for user in r.json())

def test_get_workspaces():
    r = requests.get(f"{BASE}/workspaces/")
    assert r.status_code == 200
    assert any(ws["name"] == "Test Workspace" for ws in r.json())

def test_get_databases():
    r = requests.get(f"{BASE}/databases/")
    assert r.status_code == 200
    assert any(db["name"] == "TestDB" for db in r.json())

def test_get_datasets():
    r = requests.get(f"{BASE}/datasets/")
    assert r.status_code == 200
    assert any(ds["name"] == "Test Dataset" for ds in r.json())

def test_get_charts():
    r = requests.get(f"{BASE}/charts/")
    assert r.status_code == 200
    assert any(chart["name"] == "Test Chart" for chart in r.json())

def test_get_dashboards():
    r = requests.get(f"{BASE}/dashboards/")
    assert r.status_code == 200
    assert any(dash["name"] == "Test Dashboard" for dash in r.json())

def test_get_regions():
    r = requests.get(f"{BASE}/regions/")
    assert r.status_code == 200
    assert any(region["name"] == "Test Region" for region in r.json())

def test_get_clusters():
    r = requests.get(f"{BASE}/clusters/")
    assert r.status_code == 200
    assert any(cluster["name"] == "Test Cluster" for cluster in r.json()) 