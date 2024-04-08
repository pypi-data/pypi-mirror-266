
from komodo.server.fast import prepare_fastapi_app
from sample.appliance.appliance import SampleAppliance
from sample.appliance.config import ApplianceConfig, LocalConfig


def run_server():
    import uvicorn
    uvicorn.run(SERVER, host="127.0.0.1", port=8000)  # noinspection PyTypeChecker


if __name__ == '__main__':
    SERVER = prepare_fastapi_app(SampleAppliance(LocalConfig()))
    run_server()
else:
    SERVER = prepare_fastapi_app(SampleAppliance(ApplianceConfig()))
