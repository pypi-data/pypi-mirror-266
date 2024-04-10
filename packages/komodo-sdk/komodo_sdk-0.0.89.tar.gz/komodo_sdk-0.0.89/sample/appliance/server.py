import os

from komodo.server.fast import prepare_fastapi_app
from sample.appliance.appliance import SampleAppliance
from sample.appliance.config import ApplianceConfig, LocalConfig


def build_server(config):
    server = prepare_fastapi_app(SampleAppliance(config))
    return server


def run_server():
    import uvicorn
    os.environ["KOMODO_RUN"] = "local"
    uvicorn.run("server:SERVER", host="127.0.0.1", port=8000, reload=True)  # noinspection PyTypeChecker


if __name__ == '__main__':
    run_server()
else:
    config = LocalConfig() if os.getenv("KOMODO_RUN") == "local" else ApplianceConfig()
    SERVER = build_server(config)
