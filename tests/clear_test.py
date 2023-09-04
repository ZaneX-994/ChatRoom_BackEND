from src.other import clear_v1
import requests
from src.config import url

# check the clear_v1 function works
def test_clear_v1_successful():
    assert clear_v1() is None

# check the clear_v1 function works through the /clear/v1 route
def test_clear_route_successful():
    response = requests.delete(f"{url}clear/v1")
    assert response.status_code == 200
    assert response.json() == {}
