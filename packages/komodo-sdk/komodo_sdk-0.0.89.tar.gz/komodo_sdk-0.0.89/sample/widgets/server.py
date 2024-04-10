from komodo.framework.komodo_app import KomodoApp
from sample.appliance.appliance import SampleAppliance
from sample.appliance.config import LocalConfig, ApplianceConfig
from sample.widgets.globals import set_appliance_for_dash


def build_server(config):
    server = prepare_dash_app(SampleAppliance(config))
    return server


def prepare_dash_app(appliance: KomodoApp):
    global app
    set_appliance_for_dash(appliance)
    return app


def run_server():
    set_appliance_for_dash(SampleAppliance(LocalConfig()))
    from app import app
    app.run(debug=True, port=8045)


if __name__ == '__main__':
    run_server()
else:
    prepare_dash_app(SampleAppliance(ApplianceConfig()))
