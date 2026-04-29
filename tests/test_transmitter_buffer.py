
import os
import sys
from pathlib import Path
import importlib.util
import tempfile

os.environ["TRANSMITTER_SERVER_HOST"] = "0.0.0.0"
os.environ["TRANSMITTER_SERVER_PORT"] = "5000"
os.environ["DEBUG_MODE"] = "true"
TEMP_DIR = tempfile.mkdtemp()
os.environ["TRANSMITTER_DATA_CSV"] = str(Path(TEMP_DIR) / "transmitter_data.csv")

transmitter_dir = Path(__file__).resolve().parents[1]/"transmitter"
sys.path.insert(0, str(transmitter_dir))


module_path = transmitter_dir/"transmitter-server.py"
spec = importlib.util.spec_from_file_location("transmitter_server", module_path)
transmitter_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transmitter_server)

app = transmitter_server.app

def test_hello_world():  # Test the root endpoint of the transmitter server
    client = app.test_client()
    response = client.get("/")  
    assert response.status_code == 200
    assert response.data == b"<p>Hello world from the transmitter server!</p>"


def test_start_optical_communications_persists_data():
    client = app.test_client()

    payload = {
        "experiment_id": "CO_D3.0-A0.0-I0.5-F30.0-L1.0-Mm",
        "message": "10101010",
        "settings": {
            "dummy_distance": 3.0,
            "transmitter_angle": 0.0,
            "led_intensity": 0.5,
            "blinking_frequency": 30.0,
            "messages_batch": 1.0,
        },
    }

    response = client.post("/start_optical_communications", json=payload)

    assert response.status_code == 200
    assert client.get("/get_experiment_id").data.decode() == payload["experiment_id"]
    assert client.get("/get_dummy_distance").data.decode() == str(
        payload["settings"]["dummy_distance"]
    )
    assert client.get("/get_transmitter_angle").data.decode() == str(
        payload["settings"]["transmitter_angle"]
    )
    assert client.get("/get_led_intensity").data.decode() == str(
        payload["settings"]["led_intensity"]
    )
    assert client.get("/get_messages_batch").data.decode() == str(
        payload["settings"]["messages_batch"]
    )

