from pathlib import Path

from komodo.framework.komodo_config import KomodoConfig
from sample.appliance.appliance import SampleAppliance


class ApplianceConfig(KomodoConfig):
    def __init__(self, data_directory=None, **kwargs):
        folder = Path(__file__).parent.parent.resolve()
        definitions_directory = folder / "definitions"
        super().__init__(data_directory=data_directory, definitions_directory=definitions_directory, **kwargs)

    def get_serpapi_key(self):
        return self.get_secret("SERP_API_KEY")


class LocalConfig(ApplianceConfig):
    def __init__(self):
        folder = Path(__file__).parent.parent.resolve()
        super().__init__(data_directory=folder / "data" / "komodo")


if __name__ == "__main__":
    config = LocalConfig()
    # loader = ApplianceLoader(config.definitions_directory, config.data_directory)
    # loader.setup_appliance("sample")

    sample = SampleAppliance(config)
    print(sample)
