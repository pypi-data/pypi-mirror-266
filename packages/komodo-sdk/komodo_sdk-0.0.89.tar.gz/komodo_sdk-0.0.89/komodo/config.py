from pathlib import Path

from komodo.framework.komodo_config import KomodoConfig


class PlatformConfig(KomodoConfig):

    def __init__(self):
        folder = Path(__file__).parent.resolve()
        super().__init__(data_directory=folder / "data", definitions_directory=folder / "definitions")

    def setup_custom_configuration(self):
        self.komodo_path = self.locations().appliance_data("komodo")
        self.komodo_hello_path = self.komodo_path / "dir1"
        self.komodo_inflation_path = self.komodo_path / "dir2"

    def get_mongo_url(self):
        return self.get_secret('MONGO_URL', "mongodb://root:example@localhost:27017/")

    def get_elastic_url(self):
        return self.get_secret("ELASTIC_URL", "http://localhost:9200")

    def get_authorized_indexes(self):
        return ["test-*"]

    def get_serpapi_key(self):
        return self.get_secret('SERP_API_KEY')


if __name__ == "__main__":
    config = PlatformConfig()
    print(config.get_value("data_directory"))
    print(config.get_value("definitions_directory"))
    print(config.get_mongo_url())
    print(config.get_elastic_url())
    print(config.get_authorized_indexes())
    print(config.get_serpapi_key())
