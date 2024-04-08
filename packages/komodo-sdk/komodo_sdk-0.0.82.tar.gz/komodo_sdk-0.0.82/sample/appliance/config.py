from pathlib import Path

from komodo.framework.komodo_config import KomodoConfig
from sample.appliance.appliance import SampleAppliance

APPLIANCE_FOLDER = Path(__file__).parent.parent.resolve()


class ApplianceConfig(KomodoConfig):
    def __init__(self, data_directory=None, **kwargs):
        definitions_directory = APPLIANCE_FOLDER / "definitions"
        super().__init__(data_directory=data_directory, definitions_directory=definitions_directory, **kwargs)

    def get_serpapi_key(self):
        return self.get_secret("SERP_API_KEY")


class LocalConfig(ApplianceConfig):
    def __init__(self):
        super().__init__(data_directory=APPLIANCE_FOLDER / "data" / "komodo")


if __name__ == "__main__":
    config = LocalConfig()
    # loader = ApplianceLoader(config.definitions_directory, config.data_directory)
    # loader.setup_appliance("sample")

    sample = SampleAppliance(config)
    print(sample)
